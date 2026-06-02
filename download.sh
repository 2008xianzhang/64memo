#!/usr/bin/env bash
OUT_DIR="./64memo_images"
mkdir -p "$OUT_DIR"

jq -r '.[] | "\(.[1]) \(.[0])"' ./cdx_result.json | \
while IFS=' ' read -r timestamp orig_url; do
  rel=$(echo "$orig_url" | sed 's|https\?://[^/]*/||')

  wayback_url="https://web.archive.org/web/${timestamp}im_/${orig_url}"
  dest="$OUT_DIR/$rel"
  mkdir -p "$(dirname "$dest")"

  if [[ -f "$dest" ]]; then
    echo "SKIP: $rel"
    continue
  fi

  echo "GET: $rel"
  curl -Ss -L -o "$dest" "$wayback_url" || echo "FAIL: $wayback_url"
done
