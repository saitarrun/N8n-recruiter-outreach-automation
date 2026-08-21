#!/bin/bash
set -e

# Ensure Homebrew and Node 22 LTS are in PATH
export PATH="/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# ANSI Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo -e "${CYAN}${BOLD}   🚀 Recruiter Outreach Platform — Local Turnkey Setup   ${NC}"
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""

# 1. Ensure required directories
mkdir -p files ui ~/.n8n

# 2. Sync resume PDFs if present
if [ -d "/Users/xploit404/n8n-files" ]; then
    cp -n /Users/xploit404/n8n-files/*.pdf "$DIR/files/" 2>/dev/null || true
    cp -n "$DIR/files/"*.pdf /Users/xploit404/n8n-files/ 2>/dev/null || true
fi

# 3. Start n8n Workflow Engine if not already running on port 5678
if lsof -i :5678 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ n8n Engine is already active on http://localhost:5678${NC}"
else
    echo -e "${BLUE}⚙️  Starting n8n Automation Engine...${NC}"
    nohup n8n start > "$DIR/n8n.log" 2>&1 &
    N8N_PID=$!
    echo -e "${GREEN}✓ n8n launched (PID: $N8N_PID)${NC}"
fi

# 4. Start UI Studio Server if not already running on port 3000
if lsof -i :3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Outreach Studio UI is already active on http://localhost:3000${NC}"
else
    echo -e "${BLUE}🖥️  Starting Outreach Studio Server...${NC}"
    nohup python3 "$DIR/ui/server.py" > "$DIR/ui.log" 2>&1 &
    UI_PID=$!
    echo -e "${GREEN}✓ Outreach Studio launched (PID: $UI_PID)${NC}"
fi

# 5. Wait for health check (max 5 seconds)
echo -ne "${YELLOW}⏳ Verifying services health...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo -e "\r${GREEN}✓ All services healthy & connected!                    ${NC}"
        break
    fi
    sleep 0.5
done

# 6. Auto-open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:3000
fi

echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo -e "${GREEN}${BOLD}   🎉 Platform Ready — Outreach Studio is LIVE!          ${NC}"
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""
echo -e "  ${BOLD}🖥️  Outreach Studio UI:${NC}   ${BLUE}http://localhost:3000${NC}"
echo -e "  ${BOLD}⚙️  n8n Automation:${NC}       ${BLUE}http://localhost:5678${NC}"
echo ""
echo -e "  ${BOLD}Helpful Commands:${NC}"
echo -e "  • Check Status:  ${CYAN}./status.sh${NC}"
echo -e "  • Stop Services: ${CYAN}./stop.sh${NC}"
echo -e "  • Restart:       ${CYAN}./restart.sh${NC}"
echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""
