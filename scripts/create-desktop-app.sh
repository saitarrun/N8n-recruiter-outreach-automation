#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_PATH="$HOME/Desktop/Recruiter Outreach.app"

# 1. Clean previous bundle
rm -rf "$APP_PATH"

# 2. Compile authentic native macOS Cocoa Application (Mach-O executable)
osacompile -o "$APP_PATH" -e "do shell script \"'$DIR/start.sh' > /dev/null 2>&1 &\""

# 3. Inject high-res Apple squircle icon into applet resources
if [ -f "$DIR/assets/AppIcon.icns" ]; then
    cp "$DIR/assets/AppIcon.icns" "$APP_PATH/Contents/Resources/applet.icns"
    cp "$DIR/assets/AppIcon.icns" "$APP_PATH/Contents/Resources/AppIcon.icns"
fi

# 4. Update Info.plist display name and icon mapping
if [ -f "$APP_PATH/Contents/Info.plist" ]; then
    /usr/libexec/PlistBuddy -c "Set :CFBundleName 'Recruiter Outreach'" "$APP_PATH/Contents/Info.plist" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName 'Recruiter Outreach'" "$APP_PATH/Contents/Info.plist" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c "Set :CFBundleIconFile 'applet.icns'" "$APP_PATH/Contents/Info.plist" 2>/dev/null || true
fi

# 5. Touch and register with macOS LaunchServices
touch "$APP_PATH"
if [ -x "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister" ]; then
    /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_PATH" 2>/dev/null || true
fi

echo "✓ Successfully generated compiled native macOS application: $APP_PATH"
