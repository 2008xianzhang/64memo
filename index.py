#!/usr/bin/env python3
import os, sys
from pathlib import Path

IMAGE_EXTS = {'.jpg','.jpeg','.png','.gif','.webp','.JPG','.JPEG','.PNG'}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;color:#222;font-family:sans-serif}

nav{padding:10px 16px;background:rgba(0,0,0,.04);border-bottom:1px solid rgba(0,0,0,.12);font-size:13px;position:sticky;top:0;z-index:5}
nav a{color:#666;text-decoration:none}
nav a:hover{color:#000}
nav .sep{color:#aaa;margin:0 5px}

.folders{padding:16px;display:flex;flex-wrap:wrap;gap:10px}
.folder-link{display:flex;align-items:center;gap:8px;padding:9px 15px;background:rgba(0,0,0,.04);border-radius:8px;text-decoration:none;color:#333;font-size:14px;border:1px solid rgba(0,0,0,.12)}
.folder-link:hover{background:rgba(0,0,0,.08);border-color:rgba(0,0,0,.25)}
.folder-link::before{content:"📁"}

.gallery{columns:4 180px;column-gap:6px;padding:12px}
.gallery-item{break-inside:avoid;margin-bottom:6px;display:block;cursor:zoom-in}
.gallery-item img{width:100%;display:block;border-radius:4px;transition:opacity .15s}
.gallery-item:hover img{opacity:.8}

/* ── NoScript 基础层 viewer ── */
.viewer{display:none;position:fixed;inset:0;z-index:100;flex-direction:column;background:#000}
.viewer:target{display:flex}

.v-close{position:absolute;top:12px;right:16px;z-index:10;width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;text-decoration:none;color:#fff;font-size:20px;line-height:1}
.v-close:hover{background:rgba(255,255,255,.28)}

.v-main-noscript{flex:1 1 0;min-height:0;display:flex;align-items:center;justify-content:center;position:relative}
.v-main-noscript img{max-width:100%;max-height:100%;object-fit:contain}

.v-arrow{position:absolute;top:50%;transform:translateY(-50%);width:44px;height:64px;border-radius:6px;background:rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center;text-decoration:none;color:#fff;font-size:28px;opacity:.7;transition:opacity .15s;z-index:2}
.v-arrow:hover{opacity:1;background:rgba(255,255,255,.22)}
.v-arrow.prev{left:10px}
.v-arrow.next{right:10px}

.filmstrip-noscript{flex:0 0 88px;display:flex;align-items:center;gap:6px;overflow-x:auto;padding:10px 12px;background:rgba(0,0,0,.85);border-top:1px solid rgba(255,255,255,.07);scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.2) transparent}
.thumb-ns{flex:0 0 64px;height:64px;border-radius:4px;overflow:hidden;border:2px solid transparent;opacity:.55;text-decoration:none;display:block}
.thumb-ns img{width:100%;height:100%;object-fit:cover;display:block}
.thumb-ns:hover{opacity:.85;border-color:rgba(255,255,255,.35)}
.thumb-ns.active{opacity:1;border-color:#fff;width:72px;height:72px}

/* ── JS 增强层 viewer（由 JS 动态插入） ── */
.viewer-js{display:none;position:fixed;inset:0;z-index:100;flex-direction:column;background:#000}
.viewer-js.open{display:flex}

.v-main-js{flex:1 1 0;min-height:0;overflow:hidden;position:relative}
.v-track-js{display:flex;height:100%;will-change:transform}
.v-track-js.animate{transition:transform .28s ease}
.v-slide-js{flex:0 0 100%;height:100%;display:flex;align-items:center;justify-content:center}
.v-slide-js img{max-width:100%;max-height:100%;object-fit:contain}

.filmstrip-js{flex:0 0 96px;display:flex;align-items:center;gap:6px;overflow-x:scroll;overflow-y:hidden;padding:10px 12px;background:rgba(0,0,0,.85);border-top:1px solid rgba(255,255,255,.07);-webkit-overflow-scrolling:touch;scrollbar-width:none}
.filmstrip-js::-webkit-scrollbar{display:none}
.thumb-js{flex:0 0 auto;width:64px;height:64px;border-radius:4px;overflow:hidden;border:2px solid transparent;opacity:.55;transition:width .2s,height .2s,opacity .2s,border-color .15s;display:block;cursor:pointer}
.thumb-js img{width:100%;height:100%;object-fit:cover;display:block}
.thumb-js.on{width:72px;height:72px;opacity:1;border-color:#fff}
"""

VIEWER_JS = """
(function(){
  var images = window.__gallery_images || [];
  if(!images.length) return;
  var n = images.length;

  /* 1. 隐藏所有 NoScript viewer */
  document.querySelectorAll('.viewer').forEach(function(v){ v.style.display='none'; });
  /* 阻止 :target 再显示它们 */
  var noStyle = document.createElement('style');
  noStyle.textContent = '.viewer:target{display:none}';
  document.head.appendChild(noStyle);

  /* 2. 构建单一 JS viewer */
  var vjs = document.createElement('div');
  vjs.className = 'viewer-js';

  var closeBtn = document.createElement('a');
  closeBtn.className = 'v-close';
  closeBtn.href = '#';
  closeBtn.textContent = '✕';
  closeBtn.addEventListener('click', function(e){ e.preventDefault(); close(); });
  vjs.appendChild(closeBtn);

  var vmain = document.createElement('div');
  vmain.className = 'v-main-js';

  var track = document.createElement('div');
  track.className = 'v-track-js';
  vmain.appendChild(track);

  var prevBtn = document.createElement('a');
  prevBtn.className = 'v-arrow prev';
  prevBtn.href = '#';
  prevBtn.innerHTML = '&#8249;';
  prevBtn.addEventListener('click', function(e){ e.preventDefault(); activate(cur-1, true); });
  vmain.appendChild(prevBtn);

  var nextBtn = document.createElement('a');
  nextBtn.className = 'v-arrow next';
  nextBtn.href = '#';
  nextBtn.innerHTML = '&#8250;';
  nextBtn.addEventListener('click', function(e){ e.preventDefault(); activate(cur+1, true); });
  vmain.appendChild(nextBtn);

  var film = document.createElement('div');
  film.className = 'filmstrip-js';

  images.forEach(function(src, i){
    var slide = document.createElement('div');
    slide.className = 'v-slide-js';
    var img = document.createElement('img');
    img.alt = src;
    slide.appendChild(img);
    track.appendChild(slide);

    var th = document.createElement('div');
    th.className = 'thumb-js';
    var timg = document.createElement('img');
    timg.src = src;
    timg.loading = 'lazy';
    timg.alt = src;
    th.appendChild(timg);
    th.addEventListener('click', function(){ activate(i, true); });
    film.appendChild(th);
  });

  vjs.appendChild(vmain);
  vjs.appendChild(film);
  document.body.appendChild(vjs);

  var slides = track.querySelectorAll('.v-slide-js');
  var thumbs = film.querySelectorAll('.thumb-js');
  var cur = 0;
  var loaded = {};

  function loadSlide(i){
    if(loaded[i]) return;
    loaded[i] = true;
    slides[i].querySelector('img').src = images[i];
    /* 预加载相邻 */
    [i-1, i+1].forEach(function(j){
      if(j>=0 && j<n && !loaded[j]){
        loaded[j]=true;
        slides[j].querySelector('img').src = images[j];
      }
    });
  }

  function moveTrack(i, animate){
    track.classList.toggle('animate', !!animate);
    track.style.transform = 'translateX(' + (-i * 100) + '%)';
  }

  function centerThumb(i){
    var t = thumbs[i];
    var target = t.offsetLeft - (film.clientWidth - t.offsetWidth) / 2;
    film.scrollTo({left: target, behavior:'smooth'});
  }

  function activate(i, animate){
    if(i < 0) i = 0;
    if(i > n-1) i = n-1;
    cur = i;
    loadSlide(i);
    moveTrack(i, animate);
    thumbs.forEach(function(t,j){
      t.classList.toggle('on', j===i);
    });
    centerThumb(i);
  }

  function open(i){
    vjs.classList.add('open');
    document.body.style.overflow = 'hidden';
    activate(i, false);
  }

  function close(){
    vjs.classList.remove('open');
    document.body.style.overflow = '';
    history.pushState('', document.title, window.location.pathname);
  }

  var touchX = null, touchY = null, swiping = false;
  vmain.addEventListener('touchstart', function(e){
    if(e.touches.length !== 1) { touchX = null; return; }
    touchX = e.touches[0].clientX;
    touchY = e.touches[0].clientY;
    swiping = false;
  }, {passive:true});

  vmain.addEventListener('touchmove', function(e){
    if(touchX === null) return;
    var dx = e.touches[0].clientX - touchX;
    var dy = e.touches[0].clientY - touchY;
    if(!swiping && Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 8) swiping = true;
    if(swiping && e.cancelable) e.preventDefault();
  }, {passive:false});

  vmain.addEventListener('touchend', function(e){
    if(touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX;
    var dy = e.changedTouches[0].clientY - touchY;
    touchX = null;
    var THRESH = 40;
    if(Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > THRESH){
      activate(cur + (dx < 0 ? 1 : -1), true);
    }
  }, {passive:true});

  /* 瀑布流点击拦截 */
  document.querySelectorAll('.gallery-item').forEach(function(a, i){
    a.addEventListener('click', function(e){
      e.preventDefault();
      open(i);
    });
  });

  document.addEventListener('keydown', function(e){
    if(!vjs.classList.contains('open')) return;
    if(e.key==='ArrowRight'||e.key==='ArrowDown'){ e.preventDefault(); activate(cur+1, true); }
    else if(e.key==='ArrowLeft'||e.key==='ArrowUp'){ e.preventDefault(); activate(cur-1, true); }
    else if(e.key==='Escape') close();
  });

  window.addEventListener('resize', function(){ moveTrack(cur, false); });

  /* 点击遮罩关闭（点图片外区域） */
  vmain.addEventListener('click', function(e){
    if(e.target === vmain || e.target === track) close();
  });
})();
"""

def breadcrumb(rel: Path, is_root: bool) -> str:
    if is_root: return ""
    parts = list(rel.parts)
    root_href = '../' * len(parts) + 'index.html'
    html = f'<a href="{root_href}">/</a>'
    for i, part in enumerate(parts):
        depth = len(parts) - 1 - i
        href = '../' * depth + 'index.html'
        # 首个 part 用空 sep 仅取间隙（避免与根 "/" 重复斜杠）；其余用带斜杠的分隔符
        sep = '<span class="sep"></span>' if i == 0 else '<span class="sep">/</span>'
        if i < len(parts)-1:
            html += f'{sep}<a href="{href}">{part}</a>'
        else:
            html += f'{sep}<span>{part}</span>'
    return f'<nav>{html}</nav>'

def generate_index(dirpath: Path, root: Path):
    entries = sorted(dirpath.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    subdirs = [e for e in entries if e.is_dir()]
    images  = [e for e in entries if e.is_file() and e.suffix in IMAGE_EXTS]

    rel     = dirpath.relative_to(root)
    is_root = rel == Path('.')
    title   = dirpath.name if not is_root else "64memo Archive"

    nav_html    = breadcrumb(rel, is_root)
    folder_html = ""
    if subdirs:
        links = "\n".join(
            f'<a class="folder-link" href="{d.name}/index.html">{d.name}</a>'
            for d in subdirs
        )
        folder_html = f'<div class="folders">{links}</div>'

    gallery_html = ""
    viewers_html = ""

    if images:
        n = len(images)

        # 瀑布流
        items = []
        for i, img in enumerate(images):
            items.append(
                f'<a class="gallery-item" href="#v{i}">'
                f'<img src="{img.name}" alt="{img.name}" loading="lazy"></a>'
            )
        gallery_html = '<div class="gallery">' + "\n".join(items) + "</div>"

        # NoScript viewer（每张图一个，箭头互链）
        vs = []
        for i, img in enumerate(images):
            prev_i = (i-1) % n
            next_i = (i+1) % n
            vs.append(f"""
<div class="viewer" id="v{i}">
  <a class="v-close" href="#">✕</a>
  <div class="v-main-noscript">
    <a class="v-arrow prev" href="#v{prev_i}">&#8249;</a>
    <img src="{img.name}" alt="{img.name}">
    <a class="v-arrow next" href="#v{next_i}">&#8250;</a>
  </div>
</div>""")
        viewers_html = "\n".join(vs)

        # JS 数据注入
        img_list = "[" + ",".join(f'"{img.name}"' for img in images) + "]"
        js_block = f'<script>window.__gallery_images={img_list};</script>\n<script>{VIEWER_JS}</script>'
    else:
        js_block = ""

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
{nav_html}
{folder_html}
{gallery_html}
{viewers_html}
{js_block}
</body>
</html>"""

    (dirpath / "index.html").write_text(html, encoding='utf-8')
    print(f"写入: {dirpath / 'index.html'}  ({len(images)} 张, {len(subdirs)} 目录)")

def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    for dirpath, dirnames, _ in os.walk(root):
        dirnames.sort()
        generate_index(Path(dirpath), root)
    print("✅ 完成")

if __name__ == '__main__':
    main()
