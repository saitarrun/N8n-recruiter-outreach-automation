#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# ANSI Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo -e "${CYAN}${BOLD}   🔄 Updating Recruiter Outreach Platform from GitHub   ${NC}"
echo -e "${CYAN}${BOLD}==========================================================${NC}"
echo ""

echo "1. Fetching latest updates..."
git pull --rebase origin main 2>/dev/null || git pull origin main

echo "2. Refreshing desktop application & icon..."
if [[ "$OSTYPE" == "darwin"* ]] && [ -f "$DIR/scripts/create-desktop-app.sh" ]; then
    "$DIR/scripts/create-desktop-app.sh" >/dev/null 2>&1 || true
fi

echo "3. Restarting services..."
"$DIR/restart.sh"

echo ""
echo -e "${GREEN}${BOLD}✓ Platform updated and restarted successfully!${NC}"
echo ""
