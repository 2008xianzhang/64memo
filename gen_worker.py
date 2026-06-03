#!/usr/bin/env python3
"""扫描 64memo_images/ 下真实存在的图片，生成 _worker.js。

每次访问站点根路径（及任意未命中静态资源的路径）时，worker 随机 302
跳转到其中一张图片。图片清单内联进 worker，部署时零额外请求。

用法：
    python3 gen_worker.py [IMAGES_DIR]
默认 IMAGES_DIR 为 ./64memo_images
"""
import json
import sys
from pathlib import Path

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

WORKER_TEMPLATE = """\
// 自动生成，请勿手动编辑。重新生成：python3 gen_worker.py
// 访问 /random 时返回内嵌随机图片的 HTML 页面，URL 保持在 /random，
// 刷新即可换图；右键图片可看到原始文件 URL。
const IMAGES = {images};

const esc = (s) => s.replace(/[&<>"]/g, (c) => (
  {{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }}[c]
));

const PAGE = (src, title) => `<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${{esc(title)}}</title>
<style>
  html, body {{ margin: 0; height: 100%; background: #000; }}
  body {{ display: flex; align-items: center; justify-content: center; }}
  img {{ max-width: 100%; max-height: 100vh; object-fit: contain; }}
</style>
</head>
<body>
<img src="${{src}}" alt="${{esc(title)}}">
</body>
</html>`;

export default {{
  async fetch(request, env) {{
    const url = new URL(request.url);

    if (url.pathname !== "/random" && url.pathname !== "/random/") {{
      return env.ASSETS.fetch(request);
    }}

    const pick = IMAGES[Math.floor(Math.random() * IMAGES.length)];
    const encoded = pick.split("/").map(encodeURIComponent).join("/");
    // 标题取文件名（去掉目录部分）。
    const name = pick.split("/").pop();
    // 返回内嵌该图片的页面；禁用缓存，否则刷新命中缓存看不到换图。
    return new Response(PAGE("/" + encoded, name), {{
      headers: {{
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-store, must-revalidate",
      }},
    }});
  }},
}};
"""


def main():
    images_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "./64memo_images")
    if not images_dir.is_dir():
        sys.exit(f"目录不存在: {images_dir}")

    rels = sorted(
        str(p.relative_to(images_dir)).replace("\\", "/")
        for p in images_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )
    if not rels:
        sys.exit(f"未在 {images_dir} 找到任何图片")

    # 每行一个，便于 diff
    images_literal = "[\n  " + ",\n  ".join(json.dumps(r) for r in rels) + ",\n]"
    worker = WORKER_TEMPLATE.format(images=images_literal)

    out = images_dir / "_worker.js"
    out.write_text(worker, encoding="utf-8")
    print(f"写入: {out}  ({len(rels)} 张图片)")


if __name__ == "__main__":
    main()
