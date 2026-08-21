#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}=== Recruiter Outreach Platform Status ===${NC}"

# Check UI Server
if lsof -i :3000 > /dev/null 2>&1; then
    UI_PID=$(lsof -ti :3000 | head -n 1)
    echo -e "• ${BOLD}Outreach Studio UI:${NC}   ${GREEN}ONLINE${NC} (Port 3000, PID: $UI_PID)"
else
    echo -e "• ${BOLD}Outreach Studio UI:${NC}   ${RED}OFFLINE${NC}"
fi

# Check n8n
if lsof -i :5678 > /dev/null 2>&1; then
    N8N_PID=$(lsof -ti :5678 | head -n 1)
    echo -e "• ${BOLD}n8n Workflow Engine:${NC}  ${GREEN}ONLINE${NC} (Port 5678, PID: $N8N_PID)"
else
    echo -e "• ${BOLD}n8n Workflow Engine:${NC}  ${RED}OFFLINE${NC}"
fi

# Check Health Endpoint
HEALTH=$(curl -s http://localhost:3000/api/health 2>/dev/null || true)
if [[ "$HEALTH" =~ "ok" ]]; then
    echo -e "• ${BOLD}Engine Health Proxy:${NC}  ${GREEN}CONNECTED (200 OK)${NC}"
else
    echo -e "• ${BOLD}Engine Health Proxy:${NC}  ${RED}DISCONNECTED${NC}"
fi

# Database stats
if [ -f "ui/leads.db" ]; then
    TOTAL=$(sqlite3 ui/leads.db "SELECT count(*) FROM leads;" 2>/dev/null || echo "0")
    SENT=$(sqlite3 ui/leads.db "SELECT count(*) FROM leads WHERE status='Sent';" 2>/dev/null || echo "0")
    UNSENT=$(sqlite3 ui/leads.db "SELECT count(*) FROM leads WHERE status!='Sent';" 2>/dev/null || echo "0")
    echo -e "• ${BOLD}Leads in SQLite:${NC}      ${CYAN}$TOTAL Total${NC} (${GREEN}$SENT Sent${NC}, ${YELLOW:-}$UNSENT Unsent${NC})"
fi

# Resume Library count
PDF_COUNT=$(ls -1 files/*.pdf 2>/dev/null | wc -l | tr -d ' ')
echo -e "• ${BOLD}Resume PDF Library:${NC}   ${CYAN}$PDF_COUNT resumes available${NC}"
echo ""
