"""
jd_parser.py — LLM-based Job Description parser

Prompt 2: Extract structured requirements from JD
"""
from .llm_client import LLMClient
from .models import ParsedJD

JD_PARSE_PROMPT = """You are a precise talent acquisition assistant.
Extract structured requirements from the job description below.

Return ONLY a valid JSON object with these exact keys:
{{
  "skills": ["list", "of", "required", "skills"],
  "experience": "e.g. 4-6 years",
  "role_type": "e.g. Senior ML Engineer",
  "keywords": ["important", "domain", "keywords"],
  "seniority_level": "junior | mid | senior | lead"
}}

Rules:
- skills: extract all technical skills, tools, frameworks mentioned
- experience: always express as a range string like "3-5 years"
- keywords: domain-specific buzzwords (e.g. MLOps, RAG, microservices)
- No markdown, no explanation — ONLY the JSON object

Job Description:
{jd}
"""


async def parse_jd(jd: str, client: LLMClient) -> ParsedJD:
    """
    Parse a raw job description string into structured fields using GROQ.
    Returns a ParsedJD pydantic model.
    """
    prompt = JD_PARSE_PROMPT.format(jd=jd)
    raw = await client.complete_json(prompt)

    # Safely extract fields with fallbacks
    return ParsedJD(
        skills=raw.get("skills", []),
        experience=raw.get("experience", ""),
        role_type=raw.get("role_type", ""),
        keywords=raw.get("keywords", []),
        seniority_level=raw.get("seniority_level", "mid"),
    )
