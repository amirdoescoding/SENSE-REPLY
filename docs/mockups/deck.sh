#!/bin/sh
# Render deck.html variants to PNG with Playwright's cached headless Chromium.
cd "$(dirname "$0")"
B=$(ls -d ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell | tail -1)
for v in ${V:-1 2 3}; do for s in ${S:-4 5}; do
  "$B" --headless --hide-scrollbars --allow-file-access-from-files --window-size=1920,1080 \
    --virtual-time-budget=4000 --screenshot="$PWD/deck-v$v-s$s.png" "file://$PWD/deck.html?v=$v&s=$s" 2>/dev/null
done; done
ls deck-*.png
