"""
config.py — Central configuration for TalentScout AI
"""
import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CANDIDATES_FILE = DATA_DIR / "candidates.json"

# ── GROQ / LLM ─────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "groq-1.5-mini")
GROQ_BASE    = os.getenv("GROQ_BASE", f"https://api.groq.ai/v1/models/{GROQ_MODEL}/infer")
MAX_TOKENS   = 1024

# ── Ranking weights ────────────────────────────────────────────────────────────
MATCH_WEIGHT    = 0.70   # weight of skill/experience match in final score
INTEREST_WEIGHT = 0.30   # weight of interest simulation in final score

# Skill score sub-weights
SKILL_JACCARD_W  = 0.50
SKILL_COVERAGE_W = 0.50

# Match score sub-weights
MATCH_SKILL_W   = 0.60
MATCH_EXP_W     = 0.25
MATCH_KW_BONUS  = 0.15  # max keyword bonus

# Interest default fallback
INTEREST_DEFAULTS = {"High": 0.85, "Medium": 0.55, "Low": 0.15}

# ── API ────────────────────────────────────────────────────────────────────────
DEFAULT_TOP_K = 5
MAX_TOP_K     = 15
