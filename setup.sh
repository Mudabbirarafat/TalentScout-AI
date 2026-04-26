#!/bin/bash
# setup.sh — TalentScout AI one-shot setup & run script

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       🎯  TalentScout AI  Setup          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# 1. Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌  Python3 not found. Please install Python 3.11+"
  exit 1
fi
echo -e "${GREEN}✅  Python3 found: $(python3 --version)${NC}"

# 2. Check API key
if [ -z "$GROQ_API_KEY" ]; then
  echo ""
  echo -e "${YELLOW}⚠️   GROQ_API_KEY not set.${NC}"
  echo "    Get a key at https://platform.groq.ai"
  echo "    Then run: export GROQ_API_KEY=..."
  echo ""
  read -p "    Enter your API key now (or press Enter to skip): " KEY
  if [ -n "$KEY" ]; then
    export GROQ_API_KEY="$KEY"
    echo "export GROQ_API_KEY=$KEY" >> backend/.env
    echo -e "${GREEN}✅  API key saved to backend/.env${NC}"
  fi
fi

# 3. Install dependencies
echo ""
echo -e "${CYAN}📦  Installing Python dependencies...${NC}"
cd backend
pip install -r requirements.txt -q
cd ..
echo -e "${GREEN}✅  Dependencies installed${NC}"

# 4. Start server
echo ""
echo -e "${CYAN}🚀  Starting FastAPI server on http://localhost:8000${NC}"
echo -e "${CYAN}📖  API docs at http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}TIP: Open frontend/index.html in your browser for the UI${NC}"
echo -e "${YELLOW}TIP: Run 'python scripts/test_pipeline.py --sample ml' for CLI test${NC}"
echo ""

cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
