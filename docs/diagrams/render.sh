#!/bin/sh
# Render reply-platform.html to PNG with Playwright's cached headless Chromium.
cd "$(dirname "$0")"
B=$(ls -d ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell | tail -1)
"$B" --headless --hide-scrollbars --allow-file-access-from-files --window-size=1920,1080 \
  --screenshot="$PWD/reply-platform.png" "file://$PWD/reply-platform.html" 2>/dev/null
ls -la reply-platform.png
