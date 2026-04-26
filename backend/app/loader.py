"""
loader.py — Load and validate candidates from JSON dataset
"""
import json
from functools import lru_cache
from .config import CANDIDATES_FILE
from .models import Candidate


@lru_cache(maxsize=1)
def load_candidates() -> list[Candidate]:
    """Load candidates from candidates.json, cached after first call."""
    with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Candidate(**item) for item in raw]
