#!/bin/bash
set -e

echo "=========================================================="
echo "   🚀 Recruiter Outreach Platform — Turnkey Quickstart    "
echo "=========================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Create required directories
mkdir -p files n8n_data

# If files folder is empty, copy sample files
if [ ! -f files/Sai_Tarrun_Pitta_Resume.pdf ] && [ -f /Users/xploit404/n8n-files/Sai_Tarrun_Pitta_Resume.pdf ]; then
    cp /Users/xploit404/n8n-files/*.pdf files/ 2>/dev/null || true
fi

echo "📦 Starting n8n Automation Engine and UI Studio..."
docker compose up -d

echo ""
echo "=========================================================="
echo "   🎉 All Systems Operational!                           "
echo "=========================================================="
echo ""
echo "  1. 🖥️  Open Outreach Studio UI:  http://localhost:3000"
echo "  2. ⚙️  Open n8n Automation:      http://localhost:5678"
echo ""
echo "  Quick Setup:"
echo "  - Connect your Gmail account in n8n (Credentials -> Gmail OAuth2)"
echo "  - Start composing and dispatching leads at http://localhost:3000"
echo ""
echo "=========================================================="
