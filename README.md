# 🎯 TalentScout AI
### AI-Powered Talent Scouting & Engagement Agent

> Paste a Job Description → Get a ranked candidate shortlist with match scores, interest simulation, and LLM-generated explanations — in seconds.

---

## ✨ Features

| Feature | Description |
|---|---|
| **JD Parser** | GROQ extracts skills, experience, role type, keywords, seniority from any JD |
| **Skill Matching** | Jaccard + coverage overlap scoring — transparent, fast, no embeddings needed |
| **Experience Alignment** | Smart scoring that handles underqualified and overqualified candidates |
| **Interest Simulation** | GROQ simulates candidate replies to outreach → High / Medium / Low interest |
| **Explainable Ranking** | Every score has a 2-sentence LLM-generated explanation |
| **Final Score** | `0.70 × Match + 0.30 × Interest` — auditable formula |
| **Pipeline UI** | Live step indicator showing JD Parse → Match → Interest Sim → Final Rank |
| **Zero Infrastructure** | Frontend works with just an API key — no DB, no server required |

---

## 📁 Full Project Structure

```
talentscout/
│
├── frontend/
│   └── index.html              ← Self-contained UI (open in browser, no build step)
│
├── backend/
│   ├── main.py                 ← FastAPI app with all routes
│   ├── requirements.txt        ← Python dependencies
│   ├── .env.example            ← Environment variable template
│   └── app/
│       ├── __init__.py
│       ├── config.py           ← Central config (weights, paths, model)
│       ├── models.py           ← Pydantic schemas (request/response types)
│       ├── llm_client.py       ← Async GROQ API wrapper
│       ├── loader.py           ← Candidate JSON loader (cached)
│       ├── jd_parser.py        ← LLM-based JD parser (Prompt 2)
│       ├── matcher.py          ← Skill overlap + experience scoring (Prompt 4)
│       ├── interest_sim.py     ← Interest simulation via GROQ (Prompt 5)
│       └── ranker.py           ← Final score computation (Prompt 6)
│
├── data/
│   ├── candidates.json         ← 15 diverse candidate profiles
│   └── sample_jds.json         ← Sample job descriptions for testing
│
├── scripts/
│   └── test_pipeline.py        ← CLI test script with visual output
│
├── setup.sh                    ← One-shot setup + server start
└── README.md
```

---

## ⚡ Quick Start

### Option A — Frontend Only 

1. Open `frontend/index.html` in any modern browser
2. Enter your GROQ API key (get one at [platform.groq.ai](https://platform.groq.ai))
3. Click a sample JD chip or paste your own JD
4. Choose number of results and click **⚡ Scout Talent**

No installation, no server, no build tools required.

---

### Option B — Full Backend (FastAPI)

```bash
# Clone / unzip the project
cd talentscout

# Option 1: One-shot setup script
chmod +x setup.sh
./setup.sh

# Option 2: Manual setup
cd backend
pip install -r requirements.txt

# Set your API key
export GROQ_API_KEY=...

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API runs at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

---

### Option C — CLI Test

```bash
cd talentscout
export GROQ_API_KEY=...

# Test with sample JD
python scripts/test_pipeline.py --sample ml

# Test with custom JD
python scripts/test_pipeline.py --jd "Senior Python Engineer, 5+ yrs FastAPI, Kubernetes..."

# Change number of results
python scripts/test_pipeline.py --sample nlp --top-k 3
```

---

## 🌐 API Reference

### `GET /health`
```json
{ "status": "ok", "candidates_loaded": 15, "model": "groq-1.5-mini" }
```

### `GET /candidates`
Returns all 15 candidate profiles.

### `POST /parse-jd`
```json
// Request
{ "jd": "Senior ML Engineer with 5+ years Python, TensorFlow..." }

// Response
{
  "skills": ["Python", "TensorFlow", "MLflow", "AWS SageMaker"],
  "experience": "5-7 years",
  "role_type": "Senior ML Engineer",
  "keywords": ["MLOps", "recommendation systems"],
  "seniority_level": "senior"
}
```

### `POST /scout`
```json
// Request
{ "jd": "...", "top_k": 5 }

// Response
{
  "parsed_jd": { ... },
  "total_candidates_evaluated": 15,
  "ranking_formula": "Final = 0.70 × Match + 0.30 × Interest",
  "candidates": [
    {
      "name": "Meera Pillai",
      "match_score": 0.821,
      "interest_score": 0.850,
      "final_score": 0.830,
      "interest_level": "High",
      "simulated_response": "Absolutely! I've been looking for a role...",
      "explanation": "Meera is a strong match with 6 years of production MLOps experience directly aligned with the JD requirements. She covers Python, TensorFlow, Docker, Kubernetes, and MLflow; the only gap is AWS SageMaker exposure.",
      ...
    }
  ]
}
```

Add `X-API-Key: <your GROQ API key>` header if `GROQ_API_KEY` env var is not set.

---

## 🧮 Scoring Formula

```
Match Score (0–1):
  = 0.60 × Skill Overlap
  + 0.25 × Experience Alignment
  + 0.15 × Keyword Presence (bonus, capped)

  Where:
    Skill Overlap   = 0.5 × Jaccard(JD_skills, Cand_skills)
                    + 0.5 × Coverage(JD_skills, Cand_skills)
    Exp Alignment   = 1.0  if in range
                    = 0.75 if overqualified (+3 yrs over max)
                    = ramp  if underqualified (penalized by gap)

Interest Score (0–1):
  = LLM-simulated candidate reply → High (0.75–1.0) | Medium (0.40–0.74) | Low (0.0–0.39)

Final Score:
  = 0.70 × Match Score + 0.30 × Interest Score
```

---

## 🗂️ Candidate Dataset

15 realistic Indian tech profiles covering a range of seniority and domain fit:

| ID | Name | Role | Experience | Fit Level |
|----|------|------|-----------|-----------|
| C001 | Ayesha Raza | ML Engineer | 6 yrs | Strong |
| C003 | Priya Nair | NLP / GenAI | 5 yrs | Strong (NLP JDs) |
| C010 | Rahul Gupta | ML @ Amazon | 6 yrs | Strong |
| C011 | Shruti Verma | GenAI Engineer | 4 yrs | Strong (GenAI JDs) |
| C013 | Meera Pillai | MLOps | 6 yrs | Strong (MLOps JDs) |
| C009 | Ananya Iyer | Backend | 5 yrs | Strong (Backend JDs) |
| C005 | Sneha Kapoor | Data Engineering | 5 yrs | Partial |
| C006 | Vikram Patel | Computer Vision | 3 yrs | Partial |
| C004 | Arjun Sharma | DevOps | 7 yrs | Partial |
| C015 | Tanvi Singh | NLP + Engineering | 5 yrs | Partial–Strong |
| C002 | Rohan Mehta | Frontend | 4 yrs | Weak (ML JDs) |
| C007 | Divya Menon | Product Manager | 8 yrs | Weak |
| C008 | Karan Joshi | Junior Analyst | 2 yrs | Weak |
| C012 | Nikhil Das | Systems / Rust | 7 yrs | Weak (ML JDs) |
| C014 | Aditya Bose | Java Backend | 9 yrs | Weak (Python JDs) |

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Backend | FastAPI + Uvicorn |
| LLM | GROQ (groq-1.5-mini) |
| Matching | Pure Python — Jaccard + weighted coverage |
| Data | JSON flat-file (15 candidates) |
| Concurrency | `asyncio.gather` for parallel LLM calls |

---

## 🎥 Demo Flow (3 Minutes)

1. **Open** `frontend/index.html`
2. **Click** "🤖 Senior ML Engineer" sample chip
3. **Enter** API key → click **Scout Talent**
4. **Point out** the pipeline step indicator as it advances
5. **Show** parsed JD panel (skills extracted automatically)
6. **Scroll** candidate cards — highlight animated score bars
7. **Expand** #1 card — show explanation + simulated response
8. **Switch** to "🧠 NLP / GenAI" sample — show ranking reorders entirely

---

## 💡 What Makes It Unique

1. **Interest Simulation** — Predicts candidate engagement, not just skill fit
2. **Full Explainability** — Every score is broken down and narrated
3. **Zero Infrastructure** — Single HTML file + API key = full working demo
4. **Parallel LLM Calls** — `asyncio.gather` runs explanation + interest simultaneously
5. **Transparent Formula** — `0.70 × Match + 0.30 × Interest` shown in the UI

---

*Built for Hackathon · Powered by GROQ*
