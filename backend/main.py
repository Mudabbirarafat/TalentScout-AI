"""
main.py — TalentScout AI FastAPI Application

Full pipeline:
  POST /scout  →  parse JD → match candidates → simulate interest → rank & explain
"""
import asyncio
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import DEFAULT_TOP_K, MAX_TOP_K, GROQ_MODEL
from app.models import ScoutRequest, ScoutResponse, ParseJDRequest, ParsedJD
from app.llm_client import LLMClient
from app.loader import load_candidates
from app.jd_parser import parse_jd
from app.matcher import rank_candidates_by_match, generate_explanation
from app.interest_sim import simulate_interest
from app.ranker import build_candidate_result, rank_results

# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TalentScout AI",
    description="AI-powered talent scouting & engagement agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper: get LLM client from request header or env ─────────────────────────
def _get_client(api_key: str | None) -> LLMClient:
    from app.config import GROQ_API_KEY
    key = api_key or GROQ_API_KEY
    if not key:
        raise HTTPException(
            status_code=401,
            detail="GROQ API key required. Pass X-API-Key header or set GROQ_API_KEY env var.",
        )
    return LLMClient(api_key=key)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "TalentScout AI",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/health", "/parse-jd", "/scout", "/candidates"],
    }


@app.get("/health", tags=["Health"])
async def health():
    candidates = load_candidates()
    return {
        "status": "ok",
        "candidates_loaded": len(candidates),
        "model": GROQ_MODEL,
    }


@app.get("/candidates", tags=["Data"])
async def list_candidates():
    """Return all candidate profiles in the dataset."""
    candidates = load_candidates()
    return {
        "total": len(candidates),
        "candidates": [c.model_dump() for c in candidates],
    }


@app.post("/parse-jd", tags=["Pipeline"])
async def parse_jd_endpoint(
    payload: ParseJDRequest,
    x_api_key: str | None = Header(default=None),
):
    """
    Step 1 — Parse a raw JD into structured requirements.
    Returns: skills, experience, role_type, keywords, seniority_level
    """
    client = _get_client(x_api_key)
    try:
        parsed = await parse_jd(payload.jd, client)
        return parsed.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")


@app.post("/scout", response_model=ScoutResponse, tags=["Pipeline"])
async def scout_talent(
    req: ScoutRequest,
    x_api_key: str | None = Header(default=None),
):
    """
    Full talent scouting pipeline:
    1. Parse JD → structured requirements
    2. Score all candidates → Match Score (skill overlap + experience + keywords)
    3. Take top_k × 2 candidates for LLM processing
    4. For each: generate explanation + simulate interest (in parallel)
    5. Compute Final Score = 0.70 × Match + 0.30 × Interest
    6. Return top_k ranked results
    """
    client = _get_client(x_api_key)
    top_k  = min(req.top_k or DEFAULT_TOP_K, MAX_TOP_K)

    # 1. Parse JD
    try:
        parsed_jd = await parse_jd(req.jd, client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")

    # 2. Load candidates & compute match scores
    candidates = load_candidates()
    ranked_by_match = rank_candidates_by_match(parsed_jd, candidates)

    # 3. Take 2× top_k for LLM calls (re-rank after interest)
    pre_top = ranked_by_match[: top_k * 2]

    # 4. Run explanation + interest in parallel for each candidate
    async def process_candidate(candidate, match_score):
        explanation, interest = await asyncio.gather(
            generate_explanation(parsed_jd, candidate, client),
            simulate_interest(parsed_jd, candidate, client),
        )
        return build_candidate_result(candidate, match_score, interest, explanation)

    tasks = [process_candidate(c, ms) for c, ms in pre_top]
    results = await asyncio.gather(*tasks)

    # 5. Final rank and slice
    final_ranked = rank_results(list(results))[:top_k]

    return ScoutResponse(
        parsed_jd=parsed_jd,
        total_candidates_evaluated=len(candidates),
        candidates=final_ranked,
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal error: {str(exc)}"},
    )
