"""
interest_sim.py — LLM-based candidate interest simulation

Prompt 5: Simulate candidate response to outreach + classify interest level
"""
from .config import INTEREST_DEFAULTS
from .models import Candidate, ParsedJD, InterestResult
from .llm_client import LLMClient

INTEREST_PROMPT = """You are simulating a realistic job candidate receiving a recruiter message.

Recruiter message sent to {name}:
"Hi {name}, we came across your profile and have a {role_type} opportunity that strongly aligns with your background in {top_skills}. The role involves {keywords}. Would you be open to a quick 15-minute chat to explore?"

Candidate background:
{summary}
Past roles: {roles}
Years of experience: {years}

Simulate a realistic, authentic reply from this specific candidate.
Consider: seniority, current role quality, how closely the opportunity matches their background.
Senior, well-matched candidates are cautiously positive. Weak matches are polite but uninterested.

Return ONLY valid JSON, no markdown:
{{
  "response": "1-2 sentence realistic candidate reply",
  "interest_level": "High" | "Medium" | "Low",
  "score": 0.0 to 1.0
}}

Score ranges:
  High   → 0.75 – 1.00  (excited, asks follow-up, available)
  Medium → 0.40 – 0.74  (open but cautious, needs more info)
  Low    → 0.00 – 0.39  (politely declines or unresponsive)
"""


async def simulate_interest(
    jd: ParsedJD,
    candidate: Candidate,
    client: LLMClient,
) -> InterestResult:
    """
    Simulate candidate interest using GROQ.
    Returns an InterestResult with response text, level, and numeric score.
    """
    top_skills = ", ".join(jd.skills[:4]) if jd.skills else "relevant technologies"
    keywords   = ", ".join(jd.keywords[:3]) if jd.keywords else "the domain"

    prompt = INTEREST_PROMPT.format(
        name=candidate.name,
        role_type=jd.role_type or "senior engineering",
        top_skills=top_skills,
        keywords=keywords,
        summary=candidate.short_summary,
        roles="; ".join(candidate.past_roles),
        years=candidate.years_experience,
    )

    try:
        raw = await client.complete_json(prompt)
        score = float(raw.get("score", 0.55))
        level = raw.get("interest_level", "Medium")
        response_text = raw.get("response", "Thanks for reaching out. I'd like to learn more.")

        # Clamp score to level's expected range
        score = max(0.0, min(1.0, score))

        return InterestResult(
            response=response_text,
            interest_level=level,
            score=round(score, 3),
        )
    except Exception:
        # Fallback if LLM returns malformed JSON
        return InterestResult(
            response="Thanks for reaching out. I'll review the details and get back to you.",
            interest_level="Medium",
            score=INTEREST_DEFAULTS["Medium"],
        )
