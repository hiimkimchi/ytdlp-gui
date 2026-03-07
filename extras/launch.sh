#!/usr/bin/env bash
# Entry point for the ytdlp gui .app bundle.
# The app bundle structure places this script at Contents/MacOS/launch.sh
# and the virtualenv at Contents/Resources/venv.

DIR="$(cd "$(dirname "$0")/../Resources" && pwd)"
exec "${DIR}/venv/bin/python3" -m ytdlpgui "$@"
