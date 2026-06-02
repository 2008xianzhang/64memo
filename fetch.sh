#!/usr/bin/env bash
# 爬取 Wayback Machine 中 http://www.64memo.com/pub/uploads/ 下所有存档 jpg
# 依赖：curl, jq, wget（或 aria2c）

set -euo pipefail

TARGET_URL="http://www.64memo.com/"
CDX_API="http://web.archive.org/cdx/search/cdx"

echo "[1/3] 查询 CDX 索引..."
# collapse=digest 去重（同一张图只取最早一条）
curl -Sv \
  "${CDX_API}?url=${TARGET_URL}&matchType=prefix&filter=mimetype:image/jpeg&filter=statuscode:200&collapse=digest&output=json&fl=original,timestamp&limit=100000" \
  -o ./cdx_result.json

TOTAL=$(jq 'length' ./tmp/cdx_result.json)
echo "共找到 ${TOTAL} 条记录（去重后）"
