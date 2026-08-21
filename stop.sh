#!/bin/bash

# ANSI Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}${BOLD}Shutting down Recruiter Outreach Platform...${NC}"

# Stop port 3000 (UI Server)
UI_PIDS=$(lsof -ti :3000 2>/dev/null || true)
if [ -n "$UI_PIDS" ]; then
    kill -9 $UI_PIDS 2>/dev/null || true
    echo -e "${GREEN}✓ Stopped Outreach Studio UI (port 3000)${NC}"
else
    echo -e "• Outreach Studio UI was not running."
fi

# Stop port 5678 (n8n Engine)
N8N_PIDS=$(lsof -ti :5678 2>/dev/null || true)
if [ -n "$N8N_PIDS" ]; then
    kill -9 $N8N_PIDS 2>/dev/null || true
    echo -e "${GREEN}✓ Stopped n8n Automation Engine (port 5678)${NC}"
else
    echo -e "• n8n Engine was not running."
fi

echo -e "${GREEN}✓ All services stopped.${NC}"
echo ""
