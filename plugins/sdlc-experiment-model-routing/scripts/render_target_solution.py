#!/usr/bin/env python3
"""Render the complete target-solution Markdown as a self-contained human view."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from urllib.parse import urlsplit


def safe_link(value: str) -> str | None:
    """Allow local relative links and explicit HTTP(S), never executable schemes."""
    candidate = value.strip()
    if not candidate or candidate.startswith("//") or any(ord(char) < 32 for char in candidate):
        return None
    scheme = urlsplit(candidate).scheme.lower()
    if scheme and scheme not in {"http", "https"}:
        return None
    return candidate


def slugify(value: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "section"
    slug = base
    counter = 2
    while slug in used:
        slug = f"{base}-{counter}"
        counter += 1
    used.add(slug)
    return slug


def inline_markdown(value: str) -> str:
    escaped = html.escape(value, quote=True)
    tokens: list[str] = []

    def hold(fragment: str) -> str:
        tokens.append(fragment)
        return f"\x00{len(tokens) - 1}\x00"

    escaped = re.sub(r"`([^`]+)`", lambda match: hold(f"<code>{match.group(1)}</code>"), escaped)

    def link(match: re.Match[str]) -> str:
        label, href = match.group(1), html.unescape(match.group(2))
        href = safe_link(href)
        if href is None:
            return label
        return hold(f'<a href="{html.escape(href, quote=True)}">{label}</a>')

    escaped = re.sub(r"\[([^]]+)]\(([^)]+)\)", link, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    for index, fragment in enumerate(tokens):
        escaped = escaped.replace(f"\x00{index}\x00", fragment)
    return escaped


def table_html(lines: list[str]) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in rows[1]):
        header, body = rows[0], rows[2:]
    else:
        header, body = rows[0], rows[1:]
    head = "".join(f"<th>{inline_markdown(cell)}</th>" for cell in header)
    rendered_rows = "".join(
        "<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in row) + "</tr>"
        for row in body
    )
    return f"<div class=table-wrap><table><thead><tr>{head}</tr></thead><tbody>{rendered_rows}</tbody></table></div>"


def markdown_body(source: str) -> tuple[str, list[tuple[int, str, str]], str]:
    lines = source.splitlines()
    output: list[str] = []
    headings: list[tuple[int, str, str]] = []
    title = "Target solution"
    used_slugs: set[str] = set()
    index = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{inline_markdown(' '.join(item.strip() for item in paragraph))}</p>")
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            index += 1
            continue

        fence = re.match(r"^```([^`]*)$", stripped)
        if fence:
            flush_paragraph()
            language = fence.group(1).strip()
            code: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            index += 1
            language_class = re.sub(r"[^a-zA-Z0-9_-]", "", language)
            label = f"<div class=code-label>{html.escape(language)}</div>" if language else ""
            output.append(f"<div class=code-block>{label}<pre><code class='language-{language_class}'>{html.escape(chr(10).join(code))}</code></pre></div>")
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            heading_text = re.sub(r"[*_`]", "", heading.group(2)).strip()
            slug = slugify(heading_text, used_slugs)
            if level == 1 and title == "Target solution":
                title = heading_text
            headings.append((level, heading_text, slug))
            output.append(f"<h{level} id='{slug}'>{inline_markdown(heading.group(2))}</h{level}>")
            index += 1
            continue

        if stripped.startswith("|") and "|" in stripped[1:]:
            flush_paragraph()
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            output.append(table_html(table_lines))
            continue

        if re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            items: list[str] = []
            while index < len(lines) and re.match(r"^\s*[-*]\s+", lines[index]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[index]))
                index += 1
            output.append("<ul>" + "".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "</ul>")
            continue

        if re.match(r"^[0-9]+\.\s+", stripped):
            flush_paragraph()
            items = []
            while index < len(lines) and re.match(r"^\s*[0-9]+\.\s+", lines[index]):
                items.append(re.sub(r"^\s*[0-9]+\.\s+", "", lines[index]))
                index += 1
            output.append("<ol>" + "".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "</ol>")
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            quote: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote.append(lines[index].strip().lstrip(">").strip())
                index += 1
            output.append(f"<blockquote>{inline_markdown(' '.join(quote))}</blockquote>")
            continue

        paragraph.append(line)
        index += 1

    flush_paragraph()
    return "\n".join(output), headings, title


def render_html(source: str) -> str:
    body, headings, title = markdown_body(source)
    nav_items = "".join(
        f"<li class=level-{level}><a href='#{slug}'>{html.escape(text)}</a></li>"
        for level, text, slug in headings
        if level <= 3
    )
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_title}</title><style>
:root{{--ink:#172033;--muted:#667085;--line:#d0d5dd;--paper:#f6f8fb;--card:#fff;--accent:#175cd3;--soft:#eef4ff}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.62 system-ui,-apple-system,sans-serif}}.layout{{display:grid;grid-template-columns:270px minmax(0,900px);gap:28px;max-width:1240px;margin:auto;padding:24px}}nav{{position:sticky;top:24px;align-self:start;max-height:calc(100vh - 48px);overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}}nav h2{{font-size:14px;margin:0 0 10px}}nav ul{{list-style:none;padding:0;margin:0}}nav li{{margin:6px 0}}nav li.level-3{{padding-left:14px;font-size:14px}}nav a{{color:var(--ink);text-decoration:none}}main{{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:32px 40px 56px}}.notice{{background:var(--soft);border-left:5px solid var(--accent);padding:12px 16px;margin-bottom:28px}}h1{{font-size:34px;line-height:1.2;margin-top:0}}h2{{font-size:25px;margin-top:42px;border-bottom:1px solid var(--line);padding-bottom:8px}}h3{{font-size:19px;margin-top:28px}}a{{color:var(--accent)}}code{{background:#f2f4f7;border-radius:4px;padding:.1em .3em}}pre{{overflow:auto;background:#101828;color:#f2f4f7;padding:16px;border-radius:0 0 9px 9px}}pre code{{background:none;padding:0}}.code-label{{background:#344054;color:white;padding:5px 12px;border-radius:9px 9px 0 0;font-size:12px}}.table-wrap{{overflow:auto;margin:16px 0}}table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}}th{{background:#eef2f6}}blockquote{{margin:16px 0;border-left:4px solid #98a2b3;padding:10px 15px;color:#475467;background:#f9fafb}}@media(max-width:850px){{.layout{{display:block;padding:10px}}nav{{position:static;margin-bottom:12px;max-height:none}}main{{padding:24px 18px}}}}
</style></head><body><div class=layout><nav aria-label="Document sections"><h2>Design sections</h2><ul>{nav_items}</ul></nav><main><div class=notice><b>Required reading:</b> This is the complete target solution. Nothing has been shortened or hidden.</div>{body}<p class=notice>This view is generated from <code>03-target-solution.spec.md</code>. Do not edit this HTML file.</p></main></div></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--html", type=Path, required=True)
    args = parser.parse_args()
    page = render_html(args.source.read_text(encoding="utf-8"))
    args.html.write_text(page, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
