#!/bin/sh
# Render every slide of deck.html to PNG, then join them into deck.pdf.
cd "$(dirname "$0")"
B=$(ls -d ~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell | tail -1)
ALL="0 1 2 3 4 5 6 7 8 a1 a2 a3 a4 a5 a6"
for s in ${S:-$ALL}; do
  "$B" --headless --hide-scrollbars --allow-file-access-from-files --window-size=1920,1080 \
    --virtual-time-budget=4000 --screenshot="$PWD/slide-$s.png" "file://$PWD/deck.html?s=$s" 2>/dev/null
done
{ echo '<!doctype html><style>@page{size:1920px 1080px;margin:0}body{margin:0}img{display:block;width:1920px;height:1080px;break-after:page}</style>'
  for s in $ALL; do echo "<img src=\"slide-$s.png\">"; done; } > print.html
"$B" --headless --allow-file-access-from-files --no-pdf-header-footer --print-to-pdf="$PWD/deck.pdf" "file://$PWD/print.html" 2>/dev/null
rm print.html; ls slide-*.png deck.pdf
