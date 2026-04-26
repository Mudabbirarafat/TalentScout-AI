"""
ranker.py — Final ranking engine

Prompt 6: Final Score = 0.70 × Match + 0.30 × Interest
"""
from .config import MATCH_WEIGHT, INTEREST_WEIGHT
from .models import CandidateResult, Candidate, ParsedJD, InterestResult


def compute_final_score(match_score: float, interest_score: float) -> float:
    """
    Final ranking score:
        Final = 0.70 × Match + 0.30 × Interest

    Both inputs must be in [0, 1]. Output is clamped to [0, 1].
    """
    raw = MATCH_WEIGHT * match_score + INTEREST_WEIGHT * interest_score
    return round(min(max(raw, 0.0), 1.0), 3)


def build_candidate_result(
    candidate: Candidate,
    match_score: float,
    interest: InterestResult,
    explanation: str,
) -> CandidateResult:
    """Assemble the full CandidateResult DTO."""
    final = compute_final_score(match_score, interest.score)

    return CandidateResult(
        id=candidate.id,
        name=candidate.name,
        location=candidate.location,
        education=candidate.education,
        skills=candidate.skills,
        years_experience=candidate.years_experience,
        past_roles=candidate.past_roles,
        short_summary=candidate.short_summary,
        match_score=match_score,
        interest_score=interest.score,
        final_score=final,
        interest_level=interest.interest_level,
        simulated_response=interest.response,
        explanation=explanation,
    )


def rank_results(results: list[CandidateResult]) -> list[CandidateResult]:
    """Sort results by final_score descending."""
    return sorted(results, key=lambda r: r.final_score, reverse=True)
