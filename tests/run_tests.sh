#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"

# ANSI Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo -e "${CYAN}${BOLD}   🧪 Recruiter Outreach Platform — Automated Test Suite  ${NC}"
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""

# 1. Ensure services are running before tests
if ! curl -s http://localhost:3000/api/health | grep -q "ok"; then
    echo -e "${YELLOW}⚙️  Starting local services for testing...${NC}"
    ./start.sh
fi

PYTHON_CMD="python3"
if [ -x "/opt/homebrew/bin/python3" ]; then
    PYTHON_CMD="/opt/homebrew/bin/python3"
fi

echo -e "${BLUE}1. Running Backend & Integration Test Suite (Python)...${NC}"
$PYTHON_CMD "$DIR/tests/test_platform.py"

echo ""
echo -e "${BLUE}2. Running Client-Side Parser & Logic Test Suite (Node.js)...${NC}"
node "$DIR/tests/test_client_logic.js"

echo ""
echo -e "${GREEN}${BOLD}==========================================================${NC}"
echo -e "${GREEN}${BOLD}   🎉 ALL 18 PLATFORM & SCHEDULER TESTS PASSED!           ${NC}"
echo -e "${GREEN}${BOLD}==========================================================${NC}"
echo ""
