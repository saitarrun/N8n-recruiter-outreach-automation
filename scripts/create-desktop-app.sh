#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_PATH="$HOME/Desktop/Recruiter Outreach.app"
MACOS_DIR="$APP_PATH/Contents/MacOS"
RESOURCES_DIR="$APP_PATH/Contents/Resources"

mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

# Copy high-res Apple Icon
if [ -f "$DIR/assets/AppIcon.icns" ]; then
    cp "$DIR/assets/AppIcon.icns" "$RESOURCES_DIR/AppIcon.icns"
fi

# Create Info.plist
cat << PLIST > "$APP_PATH/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>app_launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.saitarrun.recruiteroutreach</string>
    <key>CFBundleName</key>
    <string>Recruiter Outreach</string>
    <key>CFBundleDisplayName</key>
    <string>Recruiter Outreach</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# Create dynamic app launcher script
cat << LAUNCHER > "$MACOS_DIR/app_launcher"
#!/bin/bash
export PATH="/opt/homebrew/opt/node@22/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\$PATH"
"$DIR/start.sh"
LAUNCHER

chmod +x "$MACOS_DIR/app_launcher"
echo "✓ Created native Desktop application with icon: $APP_PATH"
