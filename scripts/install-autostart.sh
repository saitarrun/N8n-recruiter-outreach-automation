#!/bin/bash
set -e

PLIST_PATH="$HOME/Library/LaunchAgents/com.saitarrun.recruiteroutreach.plist"
SCRIPT_PATH="/Users/xploit404/Projects/n8n-recruiter-outreach-automation/start.sh"
mkdir -p "$HOME/Library/LaunchAgents"

cat << PLIST > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.saitarrun.recruiteroutreach</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$SCRIPT_PATH</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/xploit404/Projects/n8n-recruiter-outreach-automation/autostart.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/xploit404/Projects/n8n-recruiter-outreach-automation/autostart.err</string>
</dict>
</plist>
PLIST

launchctl load -w "$PLIST_PATH" 2>/dev/null || true
echo "✓ Installed macOS LaunchAgent! Outreach Platform will now auto-start when you log in."
