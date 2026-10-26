#!/bin/bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/DormFix"
APPS_DIR="$HOME/Applications"
TARGET="$APPS_DIR/DormFix"
APP="$APPS_DIR/DormFix.app"
STAMP="$(date +%Y%m%d-%H%M%S)"

clear
printf '%s\n' '=========================================='
printf '%s\n' ' DormFix macOS Installer'
printf '%s\n' ' Cornell SYSEN 5151 / SYSEN 5930 Demo'
printf '%s\n' '=========================================='
printf '\n'

if [ ! -d "$SRC" ]; then
  echo "ERROR: DormFix payload not found next to this installer."
  read -r -p "Press Return to close..." _
  exit 1
fi

PYTHON=""
if command -v python3 >/dev/null 2>&1; then PYTHON="$(command -v python3)"; fi
if [ -z "$PYTHON" ]; then
  echo "Python 3 was not found. DormFix requires Python 3.10+ (3.12 recommended)."
  open "https://www.python.org/downloads/macos/" 2>/dev/null || true
  read -r -p "Press Return to close..." _
  exit 1
fi
if ! "$PYTHON" - <<'PY2'
import sys
raise SystemExit(0 if sys.version_info >= (3,10) else 1)
PY2
then
  VER="$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  echo "Python $VER is too old. DormFix requires Python 3.10+."
  read -r -p "Press Return to close..." _
  exit 1
fi

mkdir -p "$APPS_DIR"
BACKUP=""
if [ -d "$TARGET" ]; then
  BACKUP="$APPS_DIR/DormFix_backup_$STAMP"
  echo "Existing DormFix installation found; moving to: $BACKUP"
  mv "$TARGET" "$BACKUP"
fi
cp -R "$SRC" "$TARGET"
mkdir -p "$TARGET/data"
if [ -n "$BACKUP" ] && [ -f "$BACKUP/data/dormfix.db" ]; then
  cp "$BACKUP/data/dormfix.db" "$TARGET/data/dormfix.db"
  echo "Preserved existing database."
fi
chmod +x "$TARGET"/*.command 2>/dev/null || true
chmod +x "$TARGET"/*.sh 2>/dev/null || true

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>DormFix</string>
<key>CFBundleDisplayName</key><string>DormFix</string>
<key>CFBundleIdentifier</key><string>edu.cornell.sysen.dormfix.demo</string>
<key>CFBundleVersion</key><string>2026.10.26</string>
<key>CFBundleShortVersionString</key><string>2026.10.26</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>DormFix</string>
<key>LSMinimumSystemVersion</key><string>11.0</string>
</dict></plist>
PLIST
cat > "$APP/Contents/MacOS/DormFix" <<'LAUNCHER'
#!/bin/bash
TARGET="$HOME/Applications/DormFix"
if [ ! -d "$TARGET" ]; then
  osascript -e 'display dialog "DormFix installation was not found in ~/Applications/DormFix." buttons {"OK"} default button "OK" with icon caution' 2>/dev/null || true
  exit 1
fi
exec /usr/bin/open -a Terminal "$TARGET/Start DormFix.command"
LAUNCHER
chmod +x "$APP/Contents/MacOS/DormFix"
# Remove quarantine only from files installed by this known package, never globally.
xattr -dr com.apple.quarantine "$TARGET" "$APP" 2>/dev/null || true

echo
echo "Running DormFix verification tests..."
cd "$TARGET"
if "$PYTHON" -m unittest discover -s tests -q; then
  echo "Verification passed."
else
  echo "WARNING: installation completed but tests reported a failure."
fi

echo
echo "Installed successfully:"
echo "  Application: $APP"
echo "  Project files: $TARGET"
echo
open "$APPS_DIR" 2>/dev/null || true
echo "You can now double-click DormFix.app."
read -r -p "Press Return to close this installer..." _
