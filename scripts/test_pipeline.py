#!/usr/bin/env python3
"""
test_pipeline.py — CLI test script for TalentScout AI backend pipeline

Usage:
  cd talent-scout
  python scripts/test_pipeline.py --jd "Senior ML Engineer with Python, TensorFlow..."
  python scripts/test_pipeline.py --sample ml
  python scripts/test_pipeline.py --sample nlp --top-k 3
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

SAMPLE_JDS = {
    "ml": """We are hiring a Senior Machine Learning Engineer.
Requirements: 5+ years Python, TensorFlow or PyTorch, AWS SageMaker, Docker/Kubernetes,
MLflow, recommendation systems or NLP experience, strong SQL skills.""",

    "nlp": """NLP / GenAI Engineer (3-6 yrs).
Skills: LangChain, RAG, HuggingFace Transformers, vector databases (FAISS, Pinecone),
Python, OpenAI API or GROQ, FastAPI for model serving.""",

    "mlops": """MLOps / AI Platform Engineer (4-7 yrs).
Skills: Python, Airflow, Kubernetes, Docker, Terraform, GCP or AWS,
MLflow model registry, CI/CD pipelines. Senior role with leadership expectations.""",

    "backend": """Senior Backend Engineer (5-8 yrs).
Skills: Python, FastAPI, PostgreSQL, Redis, Kafka, Docker, Kubernetes,
microservices, distributed systems, REST API design.""",
}


async def run(jd_text: str, top_k: int):
    from app.llm_client import LLMClient
    from app.loader import load_candidates
    from app.jd_parser import parse_jd
    from app.matcher import rank_candidates_by_match, generate_explanation
    from app.interest_sim import simulate_interest
    from app.ranker import build_candidate_result, rank_results

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        print("❌  Set GROQ_API_KEY environment variable first.")
        sys.exit(1)

    client = LLMClient(api_key=api_key)
    print(f"\n{'─'*60}")
    print("  🎯  TalentScout AI — Pipeline Test")
    print(f"{'─'*60}\n")

    # 1. Parse JD
    print("📋  Step 1/5 — Parsing Job Description...")
    jd = await parse_jd(jd_text, client)
    print(f"  Role     : {jd.role_type}")
    print(f"  Seniority: {jd.seniority_level}")
    print(f"  Exp      : {jd.experience}")
    print(f"  Skills   : {', '.join(jd.skills[:6])}{'...' if len(jd.skills)>6 else ''}")
    print(f"  Keywords : {', '.join(jd.keywords[:5])}\n")

    # 2. Match
    print("🧮  Step 2/5 — Computing match scores...")
    candidates = load_candidates()
    ranked = rank_candidates_by_match(jd, candidates)
    print(f"  Evaluated {len(candidates)} candidates → top {top_k * 2} selected\n")

    pre_top = ranked[: top_k * 2]

    # 3–4. Explain + Interest
    results = []
    for i, (c, ms) in enumerate(pre_top, 1):
        print(f"💬  Step 3–4 candidate {i}/{len(pre_top)} — {c.name}  (match={ms:.0%})")
        import asyncio
        explanation, interest = await asyncio.gather(
            generate_explanation(jd, c, client),
            simulate_interest(jd, c, client),
        )
        results.append(build_candidate_result(c, ms, interest, explanation))

    # 5. Final rank
    final = rank_results(results)[:top_k]

    print(f"\n{'═'*60}")
    print(f"  🏆  TOP {top_k} CANDIDATES")
    print(f"{'═'*60}")
    medals = ["🥇","🥈","🥉"]
    for i, r in enumerate(final):
        medal = medals[i] if i < 3 else f"#{i+1}"
        bar_m = "█" * int(r.match_score*20) + "░" * (20-int(r.match_score*20))
        bar_f = "█" * int(r.final_score*20) + "░" * (20-int(r.final_score*20))
        print(f"\n  {medal}  {r.name}  ({r.years_experience} yrs)")
        print(f"     Match    [{bar_m}] {r.match_score:.0%}")
        print(f"     Interest [{r.interest_level:<6}] {r.interest_score:.0%}")
        print(f"     Final    [{bar_f}] {r.final_score:.0%}")
        print(f"     ──")
        for line in r.explanation.strip().split('\n'):
            print(f"     {line}")
        print(f'     💬 "{r.simulated_response[:100]}{"..." if len(r.simulated_response)>100 else ""}"')

    print(f"\n{'─'*60}")
    print("  ✅  Pipeline complete!")
    print(f"  Formula: Final = 0.70×Match + 0.30×Interest")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TalentScout AI CLI Test")
    parser.add_argument("--jd",     type=str, help="Job description text")
    parser.add_argument("--sample", choices=list(SAMPLE_JDS.keys()), help="Use a sample JD")
    parser.add_argument("--top-k",  type=int, default=5, help="Number of top results (default: 5)")
    args = parser.parse_args()

    if args.sample:
        jd_text = SAMPLE_JDS[args.sample]
        print(f"Using sample JD: {args.sample}")
    elif args.jd:
        jd_text = args.jd
    else:
        print("Using default sample: ml")
        jd_text = SAMPLE_JDS["ml"]

    asyncio.run(run(jd_text, args.top_k))
