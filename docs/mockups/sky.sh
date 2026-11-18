#!/bin/sh
# Render sky.html (backdrop|dome x 10:00|18:30|23:00) to sky-<v>-<hhmm>.png
cd "$(dirname "$0")"
B=$(ls -d ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell | tail -1)
for v in ${VARIANTS:-backdrop dome}; do for t in 10:00 18:30 23:00; do
  "$B" --headless --hide-scrollbars --allow-file-access-from-files --use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader --window-size=1920,1080 \
    --virtual-time-budget=8000 --screenshot="$PWD/sky-$v-$(echo $t|tr -d :).png" "file://$PWD/sky.html?v=$v&t=$t" 2>/dev/null
done; done; ls sky-*.png
