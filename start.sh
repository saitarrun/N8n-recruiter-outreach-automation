#!/bin/bash
set -e

# ANSI Color Codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo -e "${CYAN}${BOLD}   🚀 Recruiter Outreach Platform — Turnkey Quickstart    ${NC}"
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""

# 1. Ensure required directories exist
mkdir -p files n8n_data ui

# 2. Copy .env if not exists
if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env configuration from template${NC}"
fi

# 3. Check for sample resume files
if [ ! -f files/PittaSaiTarrun_Resume.pdf ] && [ -f /Users/xploit404/n8n-files/PittaSaiTarrun_Resume.pdf ]; then
    cp /Users/xploit404/n8n-files/*.pdf files/ 2>/dev/null || true
    echo -e "${GREEN}✓ Loaded sample resume files into ./files/${NC}"
fi

# 4. Check Docker Compose availability
STARTED_DOCKER=false
if command -v docker-compose &> /dev/null && docker info &> /dev/null; then
    echo -e "${BLUE}📦 Starting platform via docker-compose...${NC}"
    docker-compose up -d
    STARTED_DOCKER=true
    echo -e "${GREEN}✓ Docker containers are running!${NC}"
elif command -v docker &> /dev/null && docker compose version &> /dev/null && docker info &> /dev/null; then
    echo -e "${BLUE}📦 Starting platform via docker compose...${NC}"
    docker compose up -d
    STARTED_DOCKER=true
    echo -e "${GREEN}✓ Docker containers are running!${NC}"
fi

if [ "$STARTED_DOCKER" = false ]; then
    echo -e "${BLUE}📦 Starting native Python UI Studio server...${NC}"
    
    # Check if UI server is already running on port 3000
    if lsof -i :3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ UI Studio is already active on http://localhost:3000${NC}"
    else
        python3 ui/server.py &
        UI_PID=$!
        echo -e "${GREEN}✓ UI Studio launched (PID: $UI_PID) on http://localhost:3000${NC}"
    fi
fi

echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo -e "${GREEN}${BOLD}   🎉 All Systems Operational!                           ${NC}"
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""
echo -e "  ${BOLD}1. 🖥️  Outreach Studio UI:${NC}  ${BLUE}http://localhost:3000${NC}"
echo -e "  ${BOLD}2. ⚙️  n8n Automation:${NC}      ${BLUE}http://localhost:5678${NC}"
echo ""
echo -e "  ${BOLD}Quick 3-Step Setup for New Users:${NC}"
echo -e "  ${CYAN}Step 1:${NC} Open ${BLUE}http://localhost:5678${NC} in your browser."
echo -e "  ${CYAN}Step 2:${NC} Connect your Gmail OAuth2 account under ${BOLD}Credentials${NC}."
echo -e "  ${CYAN}Step 3:${NC} Open ${BLUE}http://localhost:3000${NC} to start customizing and sending leads!"
echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""
