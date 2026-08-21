#!/bin/bash
PLIST_PATH="$HOME/Library/LaunchAgents/com.saitarrun.recruiteroutreach.plist"
if [ -f "$PLIST_PATH" ]; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm "$PLIST_PATH"
    echo "✓ Removed auto-start service."
else
    echo "• Auto-start service was not installed."
fi
