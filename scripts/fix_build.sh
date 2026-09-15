#!/bin/bash
# Post-build fix for Flet 0.86 macOS bundle issues.
# Flet creates ghost site-packages/ dirs without __init__.py that shadow
# the real packages in .venv/. This script removes the ghost directory.

set -e

APP_BUNDLE=$(find build/macos -name "*.app" -type d 2>/dev/null | head -1)
if [ -z "$APP_BUNDLE" ]; then
    echo "No .app bundle found in build/macos/"
    exit 1
fi

RESOURCES="$APP_BUNDLE/Contents/Resources/serious_python_darwin_serious_python_darwin.bundle/Contents/Resources"
GHOST_SITE="$RESOURCES/site-packages"

if [ -d "$GHOST_SITE" ]; then
    echo "Removing ghost site-packages/ that shadows real packages..."
    rm -rf "$GHOST_SITE"
    echo "Done."
else
    echo "No ghost site-packages found — build is fine."
fi
