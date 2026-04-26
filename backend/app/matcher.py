"""
matcher.py — Skill-based candidate matching engine

Implements:
  - Jaccard + coverage overlap for skill similarity
  - Experience alignment scoring
  - Keyword presence bonus
  - Pre-ranking before LLM explanation calls

Prompt 4: Matching explanation via LLM
"""
import re
from .config import (
    SKILL_JACCARD_W, SKILL_COVERAGE_W,
    MATCH_SKILL_W, MATCH_EXP_W, MATCH_KW_BONUS,
)
from .models import Candidate, ParsedJD
from .llm_client import LLMClient

EXPLAIN_PROMPT = """You are a talent matching specialist.

JD Required Skills: {jd_skills}
JD Role Type: {role_type}
JD Experience Required: {experience}

Candidate: {name}
Candidate Skills: {cand_skills}
Candidate Experience: {years} years
Candidate Summary: {summary}
Candidate Past Roles: {roles}

Write exactly 2 concise sentences:
1. Whether this candidate is a strong, partial, or weak match and why.
2. Key overlapping skills and the most important missing skill gaps.

Be direct and specific. No fluff."""


def _skill_overlap(jd_skills: list[str], cand_skills: list[str]) -> float:
    """
    Returns a score [0, 1] based on Jaccard + coverage average.
    Jaccard = |intersection| / |union|
    Coverage = |intersection| / |jd_skills|  (how many JD skills are covered)
    """
    if not jd_skills:
        return 0.0

    jd_set   = {s.lower().strip() for s in jd_skills}
    cand_set = {s.lower().strip() for s in cand_skills}

    intersection = jd_set & cand_set
    union        = jd_set | cand_set

    jaccard  = len(intersection) / len(union)       if union  else 0.0
    coverage = len(intersection) / len(jd_set)      if jd_set else 0.0

    return round(SKILL_JACCARD_W * jaccard + SKILL_COVERAGE_W * coverage, 4)


def _experience_score(jd_exp: str, candidate_years: int) -> float:
    """
    Score [0, 1] for experience alignment.
    Underqualified penalised, overqualified slight dip.
    """
    nums = re.findall(r"\d+", str(jd_exp))
    if not nums:
        return 0.70   # neutral fallback if no experience string

    min_exp = int(nums[0])
    max_exp = int(nums[-1]) if len(nums) > 1 else min_exp + 3

    if candidate_years < min_exp:
        gap = min_exp - candidate_years
        return max(0.0, 0.50 - 0.07 * gap)      # ramp down from 0.50
    if candidate_years > max_exp + 3:
        return 0.75                              # slightly overqualified
    return 1.0                                   # within sweet spot


def _keyword_bonus(keywords: list[str], candidate: Candidate) -> float:
    """Small bonus [0, MATCH_KW_BONUS] for keyword presence in text."""
    if not keywords:
        return 0.0
    text = (
        candidate.short_summary.lower() + " " +
        " ".join(candidate.past_roles).lower()
    )
    hits = sum(1 for kw in keywords if kw.lower() in text)
    ratio = hits / len(keywords)
    return round(min(ratio * MATCH_KW_BONUS, MATCH_KW_BONUS), 4)


def compute_match_score(jd: ParsedJD, candidate: Candidate) -> float:
    """
    Final match score [0, 1]:
      0.60 × skill_overlap + 0.25 × experience_score + keyword_bonus (max 0.15)
    """
    skill_s = _skill_overlap(jd.skills, candidate.skills)
    exp_s   = _experience_score(jd.experience, candidate.years_experience)
    kw_b    = _keyword_bonus(jd.keywords, candidate)

    raw = MATCH_SKILL_W * skill_s + MATCH_EXP_W * exp_s + kw_b
    return round(min(raw, 1.0), 3)


def rank_candidates_by_match(jd: ParsedJD, candidates: list[Candidate]) -> list[tuple[Candidate, float]]:
    """Return list of (candidate, match_score) sorted descending."""
    scored = [(c, compute_match_score(jd, c)) for c in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


async def generate_explanation(jd: ParsedJD, candidate: Candidate, client: LLMClient) -> str:
    """Generate a 2-sentence match explanation using GROQ (Prompt 4)."""
    prompt = EXPLAIN_PROMPT.format(
        jd_skills=", ".join(jd.skills),
        role_type=jd.role_type,
        experience=jd.experience,
        name=candidate.name,
        cand_skills=", ".join(candidate.skills),
        years=candidate.years_experience,
        summary=candidate.short_summary,
        roles="; ".join(candidate.past_roles),
    )
    return (await client.complete(prompt)).strip()
