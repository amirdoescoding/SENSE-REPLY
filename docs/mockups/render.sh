#!/bin/sh
# Render mock.html variants to PNG with Playwright's cached headless Chromium.
cd "$(dirname "$0")"
B=$(ls -d ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell | tail -1)
for v in 1 2 3 kpi; do
  "$B" --headless --hide-scrollbars --allow-file-access-from-files --window-size=1920,1080 \
    --virtual-time-budget=8000 --screenshot="$PWD/mock-$v.png" "file://$PWD/mock.html?v=$v" 2>/dev/null
done
ls -la mock-*.png
