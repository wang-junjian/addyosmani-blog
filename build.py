#!/usr/bin/env python3
"""
把 articles/*.md 与 README.md 构建成静态站点，输出到 _site/。

用法:
    python3 build.py            # 构建到 _site/
    python3 build.py --serve    # 构建后起本地预览服务器

依赖: markdown>=3.6  (见 requirements.txt)
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
IMAGES = ROOT / "images"
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
OUT = ROOT / "_site"

SITE_NAME = "Addy Osmani 双语存档"
SITE_URL = "https://wangjunjian.com/addyosmani-blog"
YEAR = 2026


# ---------------------------------------------------------------- markdown ---

def slugify(value: str, separator: str = "-") -> str:
    """保留中日韩字符的 slug 生成器（默认实现会把中文标题的 id 抹成空串）。"""
    value = unicodedata.normalize("NFKC", str(value)).strip().lower()
    value = re.sub(r"[^\w\u3400-\u4dbf\u4e00-\u9fff\s-]", "", value)
    value = re.sub(r"[\s_-]+", separator, value)
    value = value.strip(separator)
    return value or "section"


def new_md() -> markdown.Markdown:
    return markdown.Markdown(
        extensions=["extra", "sane_lists", "toc"],
        extension_configs={
            "toc": {"toc_depth": "2-3", "permalink": False, "slugify": slugify},
            "extra": {},
        },
        output_format="html5",
    )


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def rewrite_href(href: str) -> str:
    """仓内 .md 链接改写成站点 .html 链接。"""
    if href.startswith(("http://", "https://", "#", "mailto:")):
        return href
    if href.endswith(".md"):
        return href[: -len(".md")] + ".html"
    return href


def inline(text: str) -> str:
    """渲染行内 markdown（链接/粗体/斜体/行内代码），用于表格单元与导语。"""
    text = html.escape(text, quote=False)
    text = LINK_RE.sub(
        lambda m: f'<a href="{rewrite_href(m.group(2))}">{m.group(1)}</a>', text
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


STRAY_TAG = re.compile(r"^\s*>?\s*</(?:div|figure|figcaption|iframe|span|section|table)>\s*$", re.M)


def sanitize_md(text: str) -> str:
    """清掉采集时残留在正文里的孤立闭合标签，它们会破坏整页 HTML 结构。"""
    return STRAY_TAG.sub("", text)


STRAY_TAG = re.compile(r"^\s*>?\s*</(?:div|figure|figcaption|iframe|span|section|table)>\s*$", re.M)


def sanitize_md(text: str) -> str:
    """清掉采集时残留在正文里的孤立闭合标签，它们会破坏整页 HTML 结构。"""
    return STRAY_TAG.sub("", text)


def md_to_html(text: str) -> tuple[str, list[dict]]:
    md = new_md()
    body = md.convert(sanitize_md(text))
    return body, md.toc_tokens


# ----------------------------------------------------------------- parsing ---

META_SOURCE = re.compile(r"原文：\s*(?:\[[^\]]*\]\()?<?(https?://[^\s>)]+)", re.I)
META_DATE = re.compile(r"发布日期：\s*(\d{4}-\d{2}-\d{2})")


def parse_article(path: Path) -> dict:
    name = path.name[: -len(".md")]
    lang = "zh" if name.endswith(".zh") else "en"
    slug = name[:-3] if lang == "zh" else name

    lines = path.read_text(encoding="utf-8").split("\n")
    title = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            body_start = i + 1
            break

    head: list[str] = []
    i = body_start
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and lines[i].lstrip().startswith(">"):
        head.append(lines[i])
        i += 1
    while i < len(lines) and lines[i].strip() != "---":
        i += 1
    body = "\n".join(lines[i + 1 :]).strip()

    head_txt = "\n".join(head)
    src = META_SOURCE.search(head_txt)
    dt = META_DATE.search(head_txt)

    zh_chars = len(re.findall(r"[\u4e00-\u9fff]", body))
    en_words = len(re.findall(r"[A-Za-z][A-Za-z'-]*", body))

    return {
        "slug": slug,
        "lang": lang,
        "title": title,
        "source": src.group(1).rstrip("。.,；;") if src else "",
        "date": dt.group(1) if dt else "",
        "body": body,
        "chars": zh_chars if lang == "zh" else en_words,
        "minutes": max(1, round((zh_chars / 420) if lang == "zh" else (en_words / 230))),
        "path": path,
    }


GROUP_H3 = re.compile(r"^###\s+(.+?)\s*$")
TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_readme() -> dict:
    """从 README 抽出分类分组、推荐阅读路径、其余说明段落。"""
    text = README.read_text(encoding="utf-8")
    lines = text.split("\n")

    def find(pred, start=0):
        for i in range(start, len(lines)):
            if pred(lines[i]):
                return i
        return -1

    i_cat = find(lambda s: s.startswith("## 文章分类"))
    i_path = find(lambda s: s.startswith("## 推荐阅读路径"))
    i_rest = find(lambda s: s.startswith("## 目录结构"))

    groups: list[dict] = []
    cur: dict | None = None
    for line in lines[i_cat:i_path]:
        m = GROUP_H3.match(line)
        if m:
            heading = m.group(1)
            num, _, rest = heading.partition("、")
            cur = {
                "idx": len(groups) + 1,
                "num": num,
                "title": rest.split("（")[0].strip(),
                "count_hint": heading,
                "lede": "",
                "items": [],
                "note": "",
            }
            groups.append(cur)
            continue
        if cur is None:
            continue
        s = line.strip()
        if s and not s.startswith(("|", "#", "---")) and not cur["lede"] and not cur["items"]:
            cur["lede"] = s
        if TABLE_ROW.match(s) and "|---" not in s:
            cells = split_row(s)
            if len(cells) >= 3 and LINK_RE.search(cells[0]):
                m2 = LINK_RE.search(cells[0])
                slug = m2.group(2).split("/")[-1].replace(".zh.md", "").replace(".md", "")
                cur["items"].append(
                    {"title": m2.group(1), "slug": slug, "date": cells[1], "summary": cells[2]}
                )
        if s.startswith("**读法**"):
            cur["note"] = s

    # ---- 推荐阅读路径 ----
    path_lines = lines[i_path:i_rest]
    one_hour: list[dict] = []
    roles: list[dict] = []
    tracks: list[dict] = []

    mode = ""
    for raw in path_lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith("**如果只有"):
            mode = "hour"
            continue
        if s.startswith("**分角色"):
            mode = "roles"
            continue
        if s.startswith("**按主题"):
            mode = "tracks"
            continue
        if mode == "hour":
            m = re.match(r"^\d+\.\s+(.*)$", s)
            if m:
                item = m.group(1)
                lm = LINK_RE.search(item)
                if lm:
                    one_hour.append(
                        {
                            "title": lm.group(1),
                            "href": rewrite_href(lm.group(2)),
                            "desc": item[lm.end() :].lstrip(" —-—:").strip(),
                        }
                    )
        elif mode == "roles":
            if TABLE_ROW.match(s) and "|---" not in s:
                cells = split_row(s)
                if len(cells) == 3 and cells[0] != "你是":
                    roles.append({"who": inline(cells[0]), "start": inline(cells[1]), "then": inline(cells[2])})
        elif mode == "tracks":
            m = re.match(r"^-\s+\*\*(.+?)\*\*[：:]\s*(.*)$", s)
            if m:
                tracks.append({"name": m.group(1), "chain": inline(m.group(2))})

    rest_text = "\n".join(lines[i_rest:])
    return {"groups": groups, "one_hour": one_hour, "roles": roles, "tracks": tracks, "rest": rest_text}


# ------------------------------------------------------------- html postprod ---

def enhance_body(body: str) -> str:
    def img_repl(m: re.Match) -> str:
        tag = m.group(0)
        tag = tag.replace("<img ", '<img loading="lazy" decoding="async" class="zoomable" ', 1)
        return tag

    body = re.sub(r"<img\b[^>]*>", img_repl, body)

    def a_repl(m: re.Match) -> str:
        href = m.group(1)
        tag = m.group(0)
        if href.startswith(("http://", "https://")):
            if 'target="_blank"' not in tag:
                tag = tag.replace("<a ", '<a target="_blank" rel="noopener noreferrer" ', 1)
        return tag

    # 原文里的站内绝对路径（/blog/xxx/）在离线存档里会失效，补回站点域名
    body = re.sub(r'(href|src)="/(?!/)', r'\1="https://addyosmani.com/', body)
    # 原文里的站内绝对路径（/blog/xxx/）在离线存档里会失效，补回站点域名
    body = re.sub(r'(href|src)="/(?!/)', r'\1="https://addyosmani.com/', body)
    body = re.sub(r'<a href="([^"]*)"[^>]*>', a_repl, body)
    # 表格外层允许横向滚动
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    # 代码块包一层，便于右上角标语言
    body = re.sub(
        r'<pre><code class="language-([\w+-]+)">',
        lambda m: f'<pre data-lang="{m.group(1)}"><code class="language-{m.group(1)}">',
        body,
    )
    return body


def build_toc(tokens: list[dict]) -> str:
    if not tokens:
        return ""

    def walk(items: list[dict]) -> str:
        out = ["<ul>"]
        for t in items:
            kids = t.get("children") or []
            out.append(
                f'<li><a href="#{t["id"]}">{html.escape(t["name"])}</a>'
                + (walk(kids) if kids else "")
                + "</li>"
            )
        out.append("</ul>")
        return "".join(out)

    return walk(tokens)


# ----------------------------------------------------------------- templates ---

def esc(s: str) -> str:
    return html.escape(s, quote=True)


def head_common(*, title: str, desc: str, canonical: str, root: str, lang: str,
                og_type: str = "website", og_image: str = "") -> str:
    og_img = f'\n<meta property="og:image" content="{esc(og_image)}">' if og_image else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:url" content="{esc(canonical)}">{og_img}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#faf9f6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#151412" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/style.css">
<script>try{{var t=localStorage.getItem('ao-theme');if(t)document.documentElement.dataset.theme=t;var f=localStorage.getItem('ao-font');if(f)document.documentElement.dataset.font=f;}}catch(e){{}}</script>
</head>"""


def topbar(root: str, lang: str, *, swap_href: str = "", swap_label: str = "") -> str:
    other = "EN" if lang == "zh" else "中"
    swap = (
        f'<a class="langswap" href="{swap_href}" title="切换到{swap_label}">{other}</a>'
        if swap_href
        else ""
    )
    return f"""<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="{root}index.html">
      <span class="brand-mark">AO</span>
      <span class="brand-text">{esc(SITE_NAME)}</span>
    </a>
    <nav class="topbar-tools">
      {swap}
      <div class="seg" role="group" aria-label="字号">
        <button type="button" class="seg-btn" data-font="s" title="小字号">A</button>
        <button type="button" class="seg-btn" data-font="m" title="标准字号">A</button>
        <button type="button" class="seg-btn" data-font="l" title="大字号">A</button>
      </div>
      <button type="button" class="icon-btn" id="theme-toggle" title="切换深浅色" aria-label="切换深浅色">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.2M12 19.2v2.2M2.6 12h2.2M19.2 12h2.2M5.4 5.4l1.6 1.6M17 17l1.6 1.6M18.6 5.4L17 7M7 17l-1.6 1.6"/></svg>
      </button>
    </nav>
  </div>
</header>"""


def footer(root: str, *, home: bool = True) -> str:
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-col">
      <p class="footer-title">{esc(SITE_NAME)}</p>
      <p class="footer-note">Addy Osmani 2026 年关于智能体工程的 24 篇博客存档，中英对照。<br>
      版权归 <a href="https://addyosmani.com/" target="_blank" rel="noopener noreferrer">Addy Osmani</a> 所有，本页仅作个人学习用途，不作商业使用。</p>
    </div>
    <div class="footer-col footer-links">
      <a href="{root}index.html">全部文章</a>
      <a href="{root}about.html">收录与翻译说明</a>
      <a href="https://addyosmani.com/blog/" target="_blank" rel="noopener noreferrer">原文博客 ↗</a>
      <a href="https://github.com/wang-junjian/addyosmani-blog" target="_blank" rel="noopener noreferrer">GitHub 仓库 ↗</a>
    </div>
  </div>
</footer>"""


LIGHTBOX = """<dialog class="lightbox" id="lightbox">
  <button type="button" class="lightbox-close" aria-label="关闭">&times;</button>
  <img alt="">
</dialog>"""


# ------------------------------------------------------------------- build ---

def fmt_date(iso: str) -> str:
    try:
        d = date.fromisoformat(iso)
        return f"{d.year}.{d.month:02d}.{d.day:02d}"
    except ValueError:
        return iso


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "articles").mkdir(parents=True)
    (OUT / "assets").mkdir(parents=True)

    # --- 文章 ---
    parsed = [parse_article(p) for p in sorted(ARTICLES.glob("*.md"))]
    by_key: dict[tuple[str, str], dict] = {(a["slug"], a["lang"]): a for a in parsed}
    slugs = sorted({a["slug"] for a in parsed})

    readme = parse_readme()
    group_of: dict[str, dict] = {}
    summary_of: dict[str, str] = {}
    order: dict[str, int] = {}
    for g in readme["groups"]:
        for it in g["items"]:
            group_of[it["slug"]] = g
            summary_of[it["slug"]] = it["summary"]
            order[it["slug"]] = len(order)

    # 时间线（上一篇/下一篇）
    def _date(s: str) -> str:
        for lg in ("zh", "en"):
            if (s, lg) in by_key and by_key[(s, lg)]["date"]:
                return by_key[(s, lg)]["date"]
        return "9999-99-99"

    timeline = sorted({a["slug"] for a in parsed}, key=lambda s: (_date(s), s))

    for art in parsed:
        key = (art["slug"], art["lang"])
        other_lang = "en" if art["lang"] == "zh" else "zh"
        other = by_key.get((art["slug"], other_lang))
        body_html, toc_tokens = md_to_html(art["body"])
        body_html = enhance_body(body_html)

        group = group_of.get(art["slug"])
        summary = summary_of.get(art["slug"], "")

        if art["lang"] == "zh":
            canonical = f"{SITE_URL}/articles/{art['slug']}.zh.html"
            page_title = f"{art['title']} · {SITE_NAME}"
            alt_line = f'英文原题：{esc(other["title"])}' if other else ""
            meta_bits = [
                fmt_date(art["date"]) if art["date"] else "",
                f'约 {art["chars"]:,} 字',
                f'{art["minutes"]} 分钟',
                f'<a href="{esc(art["source"])}" target="_blank" rel="noopener noreferrer">原文 ↗</a>' if art["source"] else "",
            ]
            lang_label = "中文译文"
            swap_href = f'{art["slug"]}.html'
            swap_label = "English"
        else:
            canonical = f"{SITE_URL}/articles/{art['slug']}.html"
            page_title = f"{art['title']} · {SITE_NAME}"
            alt_line = f'中文版：{esc(other["title"])}' if other else ""
            meta_bits = [
                fmt_date(art["date"]) if art["date"] else "",
                f'{art["chars"]:,} words',
                f'{art["minutes"]} min read',
                f'<a href="{esc(art["source"])}" target="_blank" rel="noopener noreferrer">Original ↗</a>' if art["source"] else "",
            ]
            lang_label = "English"
            swap_href = f'{art["slug"]}.zh.html'
            swap_label = "中文"

        meta_line = "".join(b if b.startswith("<a") else f"<span>{b}</span>" for b in meta_bits if b)

        eyebrow = ""
        if group:
            eyebrow = (
                f'<a class="eyebrow" href="../index.html#g{group["idx"]}">'
                f'<span class="eyebrow-num">{group["idx"]:02d}</span>{esc(group["title"])}</a>'
            )

        toc_html = build_toc(toc_tokens)
        toc_block = (
            f'<aside class="toc"><div class="toc-inner"><p class="toc-title">目录</p>{toc_html}</div></aside>'
            if toc_html
            else ""
        )
        toc_mobile = (
            f'<details class="toc-mobile"><summary>目录 · {len(toc_tokens)} 节</summary>{toc_html}</details>'
            if toc_html
            else ""
        )

        # 上一篇 / 下一篇
        idx = timeline.index(art["slug"]) if art["slug"] in timeline else -1
        pager = ""
        if idx >= 0:
            prev_s = timeline[idx - 1] if idx > 0 else None
            next_s = timeline[idx + 1] if idx + 1 < len(timeline) else None
            cells = []
            for label, s in (("上一篇", prev_s), ("下一篇", next_s)):
                if s:
                    a = by_key.get((s, art["lang"])) or by_key.get((s, "zh"))
                    cells.append(
                        f'<a class="pager-card" href="{a["slug"]}{".zh" if a["lang"] == "zh" else ""}.html">'
                        f'<span class="pager-label">{label}</span>'
                        f'<span class="pager-title">{esc(a["title"])}</span></a>'
                    )
                else:
                    cells.append('<span class="pager-card is-empty"></span>')
            pager = f'<nav class="pager">{"".join(cells)}</nav>'

        og_image = ""
        m_img = re.search(r'src="(\.\./images/[^"]+)"', body_html)
        if m_img:
            og_image = f"{SITE_URL}/{m_img.group(1).replace('../', '')}"

        doc = head_common(
            title=page_title,
            desc=summary or (art["body"][:110].replace("\n", " ") if art["body"] else ""),
            canonical=canonical,
            root="../",
            lang="zh-CN" if art["lang"] == "zh" else "en",
            og_type="article",
            og_image=og_image,
        )
        doc += f"""
<body class="page-article" data-root="../">
<div class="progress" id="progress"></div>
{topbar("../", art["lang"], swap_href=swap_href, swap_label=swap_label)}
<main class="article-layout">
  <article class="prose" lang="{'zh-CN' if art['lang'] == 'zh' else 'en'}">
    <header class="article-head">
      {eyebrow}
      <h1>{esc(art["title"])}</h1>
      <p class="article-alt">{alt_line}</p>
      <div class="article-meta">{meta_line}<span class="meta-lang">{lang_label}</span></div>
    </header>
    {toc_mobile}
    {body_html}
    <hr class="article-end">
    <div class="article-foot">
      <p>本文收录自 Addy Osmani 的个人博客，中文为逐段机器翻译，术语按统一对照表处理。如遇语义偏差，以<a href="{esc(art["source"])}" target="_blank" rel="noopener noreferrer">英文原文</a>为准。</p>
    </div>
  </article>
  {toc_block}
</main>
{pager}
{footer("../")}
{LIGHTBOX}
<script src="../assets/app.js" defer></script>
</body>
</html>
"""
        (OUT / "articles" / f'{art["slug"]}{".zh" if art["lang"] == "zh" else ""}.html').write_text(doc, encoding="utf-8")

    # --- 首页 ---
    total_words_en = sum(a["chars"] for a in parsed if a["lang"] == "en")
    total_chars_zh = sum(a["chars"] for a in parsed if a["lang"] == "zh")
    n_images = len(list(IMAGES.iterdir()))

    search_index = []
    for s in slugs:
        zh, en = by_key.get((s, "zh")), by_key.get((s, "en"))
        ref = zh or en
        search_index.append(
            {
                "s": s,
                "t": ref["title"],
                "e": en["title"] if en else "",
                "d": ref["date"],
                "g": group_of[s]["title"] if s in group_of else "",
                "x": re.sub(r"\*\*|\*|`", "", summary_of.get(s, "")),
                "m": ref["minutes"],
            }
        )
    (OUT / "search.json").write_text(json.dumps(search_index, ensure_ascii=False), encoding="utf-8")

    group_html = []
    for gi, g in enumerate(readme["groups"]):
        rows = []
        for it in g["items"]:
            slug = it["slug"]
            zh, en = by_key.get((slug, "zh")), by_key.get((slug, "en"))
            ref = zh or en
            if not ref:
                continue
            rows.append(
                f"""        <li class="post" data-slug="{esc(slug)}">
          <a class="post-main" href="articles/{slug}{'.zh' if zh else ''}.html">
            <span class="post-date">{fmt_date(ref['date'])[5:] if ref['date'] else ''}</span>
            <span class="post-body">
              <span class="post-title">{inline(it['title'])}</span>
              <span class="post-sub">{esc(en['title']) if zh and en else ''}</span>
              <span class="post-summary">{inline(it['summary'])}</span>
            </span>
            <span class="post-min">{ref['minutes']}<small>min</small></span>
          </a>
          {f'<a class="post-en" href="articles/{slug}.html" title="读英文原文">EN</a>' if en else ''}
        </li>"""
            )
        note = g["note"].replace("**读法**：", "").replace("**读法**:", "")
        group_html.append(
            f"""    <section class="group" id="g{g['idx']}">
      <header class="group-head">
        <span class="group-num">{g['idx']:02d}</span>
        <div>
          <h2 class="group-title">{esc(g['title'])}</h2>
          <p class="group-lede">{inline(g['lede'])}</p>
        </div>
        <span class="group-count">{len(g['items'])} 篇</span>
      </header>
      <ol class="post-list">
{chr(10).join(rows)}
      </ol>
      {f'<p class="group-note"><span>读法</span><span class="note-body">{inline(note)}</span></p>' if note else ''}
    </section>"""
        )

    one_hour = "".join(
        f"""        <li><a href="{o['href']}">
          <span class="path-idx">{i + 1:02d}</span>
          <span class="path-title">{inline(o['title'])}</span>
          <span class="path-desc">{inline(o['desc'])}</span>
        </a></li>"""
        for i, o in enumerate(readme["one_hour"])
    )
    roles = "".join(
        f"""          <tr><th scope="row">{r['who']}</th><td>{r['start']}</td><td class="role-next">{r['then']}</td></tr>"""
        for r in readme["roles"]
    )
    tracks = "".join(
        f"""        <li><span class="track-name">{esc(t['name'])}</span><span class="track-chain">{t['chain']}</span></li>"""
        for t in readme["tracks"]
    )

    stats = [
        (str(len(slugs)), "篇文章"),
        ("双语", "中英对照"),
        (f"{total_words_en:,}", "英文词"),
        (f"{total_chars_zh // 1000}k", "中文字"),
        (f"{n_images}", "张配图"),
    ]
    stat_html = "".join(
        f'<div class="stat"><span class="stat-num">{v}</span><span class="stat-label">{k}</span></div>'
        for v, k in stats
    )

    doc = head_common(
        title=f"{SITE_NAME} · 智能体工程 24 篇",
        desc="Addy Osmani 2026 年关于智能体工程（agentic engineering）的 24 篇博客文章中英双语存档，含分类索引与推荐阅读路径。",
        canonical=f"{SITE_URL}/",
        root="",
        lang="zh-CN",
    )
    doc += f"""
<body class="page-home" data-root="">
<div class="progress" id="progress"></div>
{topbar("", "zh")}
<main>
  <section class="hero">
    <p class="hero-kicker"><span>ARCHIVE</span><span class="dot"></span>2026 · Addy Osmani</p>
    <h1 class="hero-title">智能体工程<br><em>24 篇双语存档</em></h1>
    <p class="hero-lede">Google Chrome 工程负责人 Addy Osmani 在 2026 年写下的关于 <strong>agentic engineering</strong> 的完整随笔序列——从 harness、循环、技术栈，到自主性、评审、债务与手艺。每篇含英文原文与逐段中文译文。</p>
    <div class="stats">{stat_html}</div>
    <div class="hero-actions">
      <a class="btn btn-primary" href="#g1">从分类开始</a>
      <a class="btn" href="#paths">推荐阅读路径</a>
      <a class="btn btn-ghost" href="about.html">收录与翻译说明</a>
    </div>
  </section>

  <div class="searchbar" id="searchbar">
    <div class="searchbar-inner">
      <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg>
      <input type="search" id="search-input" placeholder="搜索标题、主旨或分类…（按 / 聚焦）" autocomplete="off" spellcheck="false">
      <kbd class="search-kbd">/</kbd>
      <button type="button" class="search-clear" id="search-clear" aria-label="清空" hidden>&times;</button>
    </div>
    <div class="search-results" id="search-results" hidden></div>
  </div>

  <div id="groups">
{chr(10).join(group_html)}
  </div>

  <section class="paths" id="paths">
    <header class="section-head">
      <h2>推荐阅读路径</h2>
      <p>二十四篇不必按顺序读。这里给出三条入口：时间有限就走第一条，按角色定位走第二条，想追一条完整的思考线走第三条。</p>
    </header>

    <div class="path-grid">
      <div class="path-card">
        <p class="path-card-title">如果只有一个小时<small>约 1.3 万字</small></p>
        <ol class="path-list">
{one_hour}
        </ol>
      </div>
      <div class="path-card path-card-wide">
        <p class="path-card-title">分角色的入口</p>
        <div class="table-wrap">
          <table class="role-table">
            <thead><tr><th>你是</th><th>从这里开始</th><th>然后</th></tr></thead>
            <tbody>
{roles}
            </tbody>
          </table>
        </div>
      </div>
      <div class="path-card path-card-wide">
        <p class="path-card-title">按主题纵向追一条线</p>
        <ul class="track-list">
{tracks}
        </ul>
      </div>
    </div>
  </section>
</main>
{footer("")}
<script src="assets/app.js" defer></script>
</body>
</html>
"""
    (OUT / "index.html").write_text(doc, encoding="utf-8")

    # --- about ---
    rest_html, _ = md_to_html(readme["rest"])
    rest_html = enhance_body(rest_html)
    rest_html = re.sub(r"<h2>", '<h2 class="about-h2">', rest_html)
    doc = head_common(
        title=f"收录与翻译说明 · {SITE_NAME}",
        desc="这 24 篇是怎么采集的、怎么翻译的、质检口径是什么，以及已知的边界。",
        canonical=f"{SITE_URL}/about.html",
        root="",
        lang="zh-CN",
    )
    doc += f"""
<body class="page-article" data-root="">
<div class="progress" id="progress"></div>
{topbar("", "zh")}
<main class="article-layout article-layout--plain">
  <article class="prose">
    <header class="article-head">
      <a class="eyebrow" href="index.html"><span class="eyebrow-num">i</span>关于这个存档</a>
      <h1>收录与翻译说明</h1>
      <p class="article-alt">采集范围、格式转换、翻译规则与质检口径，以及这套存档的已知边界。</p>
    </header>
    {rest_html}
  </article>
</main>
{footer("")}
<script src="assets/app.js" defer></script>
</body>
</html>
"""
    (OUT / "about.html").write_text(doc, encoding="utf-8")

    # --- 静态资源 ---
    shutil.copytree(IMAGES, OUT / "images")
    for name in ("style.css", "app.js", "favicon.svg"):
        src = ASSETS / name
        if src.exists():
            shutil.copy2(src, OUT / "assets" / name)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )

    # sitemap
    urls = [f"{SITE_URL}/", f"{SITE_URL}/about.html"]
    for a in parsed:
        urls.append(f"{SITE_URL}/articles/{a['slug']}{'.zh' if a['lang'] == 'zh' else ''}.html")
    entries = "\n".join(
        f"  <url><loc>{esc(u)}</loc></url>" for u in urls
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n',
        encoding="utf-8",
    )

    n_pages = len(list(OUT.rglob("*.html")))
    print(f"✓ 构建完成：{n_pages} 个页面 → {OUT.relative_to(ROOT)}/")
    print(f"  文章 {len(parsed)} 篇（{len(slugs)} 组双语）· 图片 {n_images} 张 · 索引 {len(search_index)} 条")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true", help="构建后启动本地预览")
    ap.add_argument("--port", type=int, default=8777)
    args = ap.parse_args()

    build()
    if args.serve:
        import functools
        import http.server
        import socketserver

        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
            print(f"  预览: http://127.0.0.1:{args.port}/  (Ctrl-C 退出)")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    sys.exit(main())
