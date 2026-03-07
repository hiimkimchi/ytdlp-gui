#!/usr/bin/env bash
# build_app.sh — assembles ytdlpgui.app for macOS
# Run from the repo root: ./extras/build_app.sh

set -euo pipefail

APP_NAME="ytdlp gui"
APP_DIR="dist/${APP_NAME}.app"
CONTENTS="${APP_DIR}/Contents"
MACOS="${CONTENTS}/MacOS"
RESOURCES="${CONTENTS}/Resources"

echo "→ Cleaning dist/"
rm -rf "dist/"
mkdir -p "$MACOS" "$RESOURCES"

echo "→ Copying Info.plist"
cp extras/Info.plist "${CONTENTS}/Info.plist"

echo "→ Creating launch script"
cp extras/launch.sh "${MACOS}/launch.sh"
chmod +x "${MACOS}/launch.sh"

echo "→ Installing package into app venv"
python3 -m venv "${RESOURCES}/venv"
"${RESOURCES}/venv/bin/pip" install --quiet --upgrade pip
"${RESOURCES}/venv/bin/pip" install --quiet .

echo ""
echo "✓ Built: ${APP_DIR}"
echo ""
echo "  To install:  cp -r \"${APP_DIR}\" /Applications/"
echo "  To run:      open \"${APP_DIR}\""
