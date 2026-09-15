#!/bin/bash
# Build DevCodex macOS app.
# Uses --no-compile-packages to avoid Flet 0.86 ghost site-packages bug
# where compiled .pyc files in .venv can't be found when ghost dirs shadow them.

set -e

echo "Cleaning old build..."
rm -rf build/macos

echo "Building macOS app..."
flet build macos --no-compile-packages

APP_BUNDLE=$(find build/macos -name "*.app" -type d 2>/dev/null | head -1)
if [ -z "$APP_BUNDLE" ]; then
    echo "ERROR: Build failed — no .app bundle found."
    exit 1
fi

echo ""
echo "Build complete: $APP_BUNDLE"
echo "Open with: open \"$APP_BUNDLE\""
