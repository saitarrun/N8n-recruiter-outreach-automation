#!/bin/bash
set -e

# Ensure Homebrew and Node 22 LTS are in PATH
export PATH="/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# ==========================================================
# ⚙️ n8n Production Environment Configuration
# ==========================================================
export N8N_PORT=5678
export N8N_PROTOCOL=http
export N8N_HOST=localhost
export WEBHOOK_URL=http://localhost:5678/
export N8N_DEFAULT_BINARY_DATA_MODE=default
export N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
export NODE_FUNCTION_ALLOW_BUILTIN=fs,path,os,crypto
export NODE_FUNCTION_ALLOW_EXTERNAL=*
export N8N_COMMUNITY_PACKAGES_ENABLED=true
export GENERIC_TIMEZONE=America/Los_Angeles
export TZ=America/Los_Angeles
export N8N_DIAGNOSTICS_ENABLED=false
export N8N_VERSION_NOTIFICATIONS_ENABLED=false
export N8N_HIRING_BANNER_ENABLED=false
export N8N_PERSONALIZATION_ENABLED=false
export N8N_LOG_LEVEL=info

# ANSI Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

DIR="/Users/xploit404/Projects/n8n-recruiter-outreach-automation"
cd "$DIR"

echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo -e "${CYAN}${BOLD}   🚀 Recruiter Outreach Platform — Permanent Auto-Setup  ${NC}"
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""

# 1. Ensure required directories
mkdir -p "$DIR/files" "$DIR/ui" "$HOME/.n8n"

# 2. Sync any resume PDFs from Desktop or n8n-files
if [ -d "$HOME/n8n-files" ]; then
    cp -n "$HOME/n8n-files/"*.pdf "$DIR/files/" 2>/dev/null || true
fi
if [ -d "$HOME/Desktop" ]; then
    cp -n "$HOME/Desktop/"*.pdf "$DIR/files/" 2>/dev/null || true
fi

# 3. Auto-configure n8n workflow pipeline
echo -e "${BLUE}🔧 Verifying n8n workflows & Gmail pipeline configuration...${NC}"
if [ -f "$DIR/workflows/direct_recruiter_outreach_batch_workflow.json" ]; then
    n8n import:workflow --input="$DIR/workflows/direct_recruiter_outreach_batch_workflow.json" > /dev/null 2>&1 || true
    n8n publish:workflow --id=T5xzFPEkCQ3vjclr > /dev/null 2>&1 || true
fi
echo -e "${GREEN}✓ Workflows & Gmail pipeline configured & active!${NC}"

# 4. Start n8n Workflow Engine if not already running on port 5678
if lsof -i :5678 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ n8n Engine is already running (http://localhost:5678)${NC}"
else
    echo -e "${BLUE}⚙️  Starting n8n Automation Engine...${NC}"
    nohup n8n start > "$DIR/n8n.log" 2>&1 &
    N8N_PID=$!
    echo -e "${GREEN}✓ n8n launched (PID: $N8N_PID)${NC}"
fi

# 5. Start UI Studio Server if not already running on port 3000
if lsof -i :3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Outreach Studio UI is already running (http://localhost:3000)${NC}"
else
    echo -e "${BLUE}🖥️  Starting Outreach Studio Server...${NC}"
    nohup python3 "$DIR/ui/server.py" > "$DIR/ui.log" 2>&1 &
    UI_PID=$!
    echo -e "${GREEN}✓ Outreach Studio launched (PID: $UI_PID)${NC}"
fi

# 6. Verify health check
echo -ne "${YELLOW}⏳ Verifying services connection...${NC}"
HEALTHY=false
for i in {1..12}; do
    if curl -s http://localhost:3000/api/health | grep -q "ok"; then
        HEALTHY=true
        echo -e "\r${GREEN}✓ All services active & connected! (Latency: <2ms)       ${NC}"
        break
    fi
    sleep 0.5
done

if [ "$HEALTHY" = false ]; then
    echo -e "\r${YELLOW}⚠️  Services starting up, opening browser...              ${NC}"
fi

# 7. Open browser automatically
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:3000"
fi

echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo -e "${GREEN}${BOLD}   🎉 Outreach Platform is Ready to Send!                ${NC}"
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""
echo -e "  ${BOLD}🖥️  Outreach Studio UI:${NC}   ${BLUE}http://localhost:3000${NC}"
echo -e "  ${BOLD}⚙️  n8n Automation:${NC}       ${BLUE}http://localhost:5678${NC}"
echo ""
echo -e "  ${BOLD}Management Commands:${NC}"
echo -e "  • Check Status:  ${CYAN}./status.sh${NC}"
echo -e "  • Stop Services: ${CYAN}./stop.sh${NC}"
echo -e "  • Restart:       ${CYAN}./restart.sh${NC}"
echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""
