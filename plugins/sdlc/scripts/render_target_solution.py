#!/usr/bin/env python3
"""Render the complete target-solution Markdown as a self-contained human view."""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from artifact_view import SOURCE_PREVIEW_CSS, markdown_body


def render_html(source: str) -> str:
    body, headings, title = markdown_body(source)
    nav_items = "".join(
        f"<li class=level-{level}><a href='#{slug}'>{html.escape(text)}</a></li>"
        for level, text, slug in headings
        if level <= 3
    )
    safe_title = html.escape(title)
    preview_css = SOURCE_PREVIEW_CSS if 'class="source-preview"' in body else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_title}</title><style>
:root{{--ink:#172033;--muted:#667085;--line:#d0d5dd;--paper:#f6f8fb;--card:#fff;--accent:#175cd3;--soft:#eef4ff}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.62 system-ui,-apple-system,sans-serif}}.layout{{display:grid;grid-template-columns:270px minmax(0,900px);gap:28px;max-width:1240px;margin:auto;padding:24px}}nav{{position:sticky;top:24px;align-self:start;max-height:calc(100vh - 48px);overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}}nav h2{{font-size:14px;margin:0 0 10px}}nav ul{{list-style:none;padding:0;margin:0}}nav li{{margin:6px 0}}nav li.level-3{{padding-left:14px;font-size:14px}}nav a{{color:var(--ink);text-decoration:none}}main{{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:32px 40px 56px}}.notice{{background:var(--soft);border-left:5px solid var(--accent);padding:12px 16px;margin-bottom:28px}}h1{{font-size:34px;line-height:1.2;margin-top:0}}h2{{font-size:25px;margin-top:42px;border-bottom:1px solid var(--line);padding-bottom:8px}}h3{{font-size:19px;margin-top:28px}}a{{color:var(--accent)}}code{{background:#f2f4f7;border-radius:4px;padding:.1em .3em}}pre{{overflow:auto;background:#101828;color:#f2f4f7;padding:16px;border-radius:0 0 9px 9px}}pre code{{background:none;padding:0}}.code-label{{background:#344054;color:white;padding:5px 12px;border-radius:9px 9px 0 0;font-size:12px}}.table-wrap{{overflow:auto;margin:16px 0}}table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}}th{{background:#eef2f6}}blockquote{{margin:16px 0;border-left:4px solid #98a2b3;padding:10px 15px;color:#475467;background:#f9fafb}}@media(max-width:850px){{.layout{{display:block;padding:10px}}nav{{position:static;margin-bottom:12px;max-height:none}}main{{padding:24px 18px}}}}
{preview_css}</style></head><body><div class=layout><nav aria-label="Document sections"><h2>Design sections</h2><ul>{nav_items}</ul></nav><main><div class=notice><b>Required reading:</b> This is the complete target solution. Nothing has been shortened or hidden.</div>{body}<p class=notice>This view is generated from <code>03-target-solution.spec.md</code>. Do not edit this HTML file.</p></main></div></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--html", type=Path, required=True)
    args = parser.parse_args()
    try:
        page = render_html(args.source.read_text(encoding="utf-8"))
        args.html.write_text(page, encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
