"""
models.py — Pydantic schemas for TalentScout AI
"""
from typing import Optional
from pydantic import BaseModel, Field


# ── Request models ─────────────────────────────────────────────────────────────

class ScoutRequest(BaseModel):
    jd: str = Field(..., min_length=20, description="Full job description text")
    top_k: Optional[int] = Field(5, ge=1, le=15, description="Number of candidates to return")


class ParseJDRequest(BaseModel):
    jd: str = Field(..., min_length=20)


# ── Parsed JD ──────────────────────────────────────────────────────────────────

class ParsedJD(BaseModel):
    skills: list[str] = []
    experience: str = ""
    role_type: str = ""
    keywords: list[str] = []
    seniority_level: str = ""


# ── Candidate (raw, from dataset) ─────────────────────────────────────────────

class Candidate(BaseModel):
    id: str
    name: str
    skills: list[str]
    years_experience: int
    past_roles: list[str]
    short_summary: str
    location: Optional[str] = ""
    education: Optional[str] = ""


# ── Interest simulation output ─────────────────────────────────────────────────

class InterestResult(BaseModel):
    response: str
    interest_level: str   # "High" | "Medium" | "Low"
    score: float          # 0.0 – 1.0


# ── Final candidate result ─────────────────────────────────────────────────────

class CandidateResult(BaseModel):
    id: str
    name: str
    location: Optional[str] = ""
    education: Optional[str] = ""
    skills: list[str]
    years_experience: int
    past_roles: list[str]
    short_summary: str
    match_score: float
    interest_score: float
    final_score: float
    interest_level: str
    simulated_response: str
    explanation: str


# ── Full scout response ────────────────────────────────────────────────────────

class ScoutResponse(BaseModel):
    parsed_jd: ParsedJD
    total_candidates_evaluated: int
    candidates: list[CandidateResult]
    ranking_formula: str = "Final = 0.70 × Match + 0.30 × Interest"
