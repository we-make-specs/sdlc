#!/usr/bin/env python3
"""Render a complete question inventory with derived progress labels."""

from __future__ import annotations

import argparse
import html
import re
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import artifact_view


QUESTION = re.compile(r"^Q([0-9]+)(?=\s|[:.])", re.IGNORECASE)
FIELD = re.compile(r"^\s*(?:[-*+]\s+)?(?:\*\*([^*]+?)\*\*\s*:?|([^:*]+):)\s*(.*)$")
PLACEHOLDER = re.compile(r"^(?:open|unanswered|pending|tbd|todo|not answered)(?:\s*[:.].*)?$", re.IGNORECASE)
VERIFIED = re.compile(r"^(?:verified|confirmed)\s+by\s+\S(?:.*?\S)?\s+on\s+\d{4}-\d{2}-\d{2}(?:\b|$)", re.IGNORECASE)
INPUT_NOT_REQUIRED = re.compile(r"^not required\s+by\s+\S(?:.*?\S)?\s+on\s+\d{4}-\d{2}-\d{2}\s*;\s*\S", re.IGNORECASE)
STATUSES = ("Open", "Needs confirmation", "Answered")


def plain_value(value: str) -> str:
    return re.sub(r"[*_`]", "", value).strip().strip("<>[] ")


def question_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, list[str]] = {}
    current: str | None = None
    field_indent = 0
    for index, line in artifact_view.markdown_content_lines(lines):
        indent = len(lines[index]) - len(lines[index].lstrip())
        match = FIELD.match(line)
        if match:
            key = (match.group(1) or match.group(2)).strip().rstrip(": ").casefold()
            if key in {"answer", "confirmation", "input verification", "category", "needed from"}:
                if key in fields:
                    raise ValueError(f"duplicate {key} field in one question; append corrections as a new Q<n> entry")
                fields[key] = [match.group(3)]
                current = key
                field_indent = indent
                continue
        if not line.strip():
            continue
        if current is not None and indent > field_indent and not artifact_view.HEADING.match(line):
            fields[current].append(line.strip())
        else:
            current = None
    return {key: plain_value(" ".join(parts)) for key, parts in fields.items()}


def answer_status(fields: dict[str, str]) -> str:
    answer = fields.get("answer", "")
    verification = fields.get("input verification", "")
    category = fields.get("category", "").replace("-", " ").casefold()
    missing_input = "missing input" in category
    if (verification or missing_input) and not (VERIFIED.match(verification) or INPUT_NOT_REQUIRED.match(verification)):
        return "Open"
    if not answer or PLACEHOLDER.fullmatch(answer) or answer.startswith(("…", "...")):
        return "Open"
    confirmation = fields.get("confirmation", "")
    if confirmation and not VERIFIED.match(confirmation):
        return "Needs confirmation"
    if re.match(r"^(?:assumed|assumption|proposed)\b", answer, re.IGNORECASE) and not VERIFIED.match(confirmation):
        return "Needs confirmation"
    return "Answered"


def question_entries(source: str) -> list[dict[str, str]]:
    lines = source.splitlines()
    headings: list[tuple[int, int, str]] = []
    for index, line in artifact_view.markdown_content_lines(lines):
        heading = artifact_view.HEADING.match(line)
        if heading:
            headings.append((index, len(heading.group(1)), re.sub(r"[*_`]", "", heading.group(2)).strip()))

    entries = []
    ids: set[str] = set()
    for position, (line_index, level, title) in enumerate(headings):
        match = QUESTION.match(title)
        if not match:
            continue
        question_id = "Q" + match.group(1)
        if question_id in ids:
            raise ValueError(f"duplicate question ID: {question_id}")
        ids.add(question_id)
        end = next((index for index, next_level, _ in headings[position + 1:] if next_level <= level), len(lines))
        fields = question_fields(lines[line_index + 1:end])
        entries.append({"id": question_id, "title": title, "status": answer_status(fields)})
    return entries


def badge(status: str) -> str:
    style = {"Open": "open", "Needs confirmation": "confirmation", "Answered": "answered"}[status]
    return f'<span class="status {style}">{status}</span>'


def render_html(source: str, *, title: str | None = None) -> str:
    entries = question_entries(source)
    body, headings, source_title = artifact_view.markdown_body(source, default_title="Questions")
    by_title = {entry["title"]: entry for entry in entries}
    navigation = []
    for level, text, slug in headings:
        entry = by_title.get(text)
        if entry:
            label = re.sub(r"\[[^]]+]\s*", "", text)
            navigation.append(f'<li><a href="#{slug}"><span>{html.escape(label)}</span>{badge(entry["status"])}</a></li>')
            opening = f"<h{level} id='{slug}'>"
            body = body.replace(opening, opening + '<span class="question-icon" aria-hidden="true">?</span>', 1)
            ending = f"</h{level}>"
            start = body.index(opening)
            end = body.index(ending, start)
            body = body[:end] + " " + badge(entry["status"]) + body[end:]

    counts = Counter(entry["status"] for entry in entries)
    summary = "".join(f'<span><b>{counts[status]}</b> {status.lower()}</span>' for status in STATUSES)
    sections = "".join(f'<li><a href="#{slug}">{html.escape(text)}</a></li>' for level, text, slug in headings
                       if level == 2 and text not in by_title)
    page_title = html.escape(title or source_title)
    preview_css = getattr(artifact_view, "SOURCE_PREVIEW_CSS", "")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark"><title>{page_title}</title>
<style>
:root{{--ink:#172b43;--muted:#52657c;--line:#cdd9e5;--paper:#f3f6fa;--card:#fff;--accent:#1566c2;--soft:#e9f2ff;--green:#256d42;--green-soft:#eaf5ed;--pink:#9b296c;--pink-soft:#faedf5}}
@media(prefers-color-scheme:dark){{:root{{--ink:#e1eaf4;--muted:#acbed3;--line:#3a4d65;--paper:#131d29;--card:#1c2939;--accent:#8bbfff;--soft:#203c60;--green:#9cd5b2;--green-soft:#214537;--pink:#efafd3;--pink-soft:#4b2a43}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 "Avenir Next","Segoe UI",sans-serif}}a{{color:var(--accent);text-underline-offset:3px}}a:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}}
.layout{{display:grid;grid-template-columns:245px minmax(0,920px);gap:24px;max-width:1240px;margin:auto;padding:24px}}nav{{position:sticky;top:24px;align-self:start;max-height:calc(100vh - 48px);overflow:auto}}nav h2{{font-size:14px;margin:0 0 10px}}nav ul{{list-style:none;padding:0;margin:0}}nav li{{margin:4px 0}}nav a{{display:flex;flex-wrap:wrap;gap:5px 10px;padding:8px;text-decoration:none;color:var(--ink);font-size:12px;border:1px solid transparent;border-radius:4px}}nav a:hover{{background:var(--card);border-color:var(--line)}}nav a>span:first-child{{flex-basis:100%}}nav .sections{{border-top:1px solid var(--line);padding-top:12px;margin-top:20px}}
main{{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:28px 32px 40px;overflow-wrap:break-word}}h1{{font-size:28px;line-height:1.25}}h2{{font-size:22px;margin:36px 0 15px;border-bottom:1px solid var(--line);padding-bottom:8px}}h3{{font-size:18px;line-height:1.5;margin:30px 0 12px;scroll-margin-top:20px}}h4{{font-size:16px}}p{{max-width:85ch}}li{{margin:5px 0}}code{{background:var(--paper);border-radius:3px;padding:2px 4px;overflow-wrap:anywhere;font-size:.88em}}pre{{overflow:auto;background:var(--paper);border:1px solid var(--line);padding:14px}}pre code{{padding:0;background:none}}.code-label{{font-size:12px;color:var(--muted)}}.table-wrap{{overflow:auto;margin:16px 0}}table{{width:100%;border-collapse:collapse;font-size:13px;line-height:1.55}}th,td{{border:1px solid var(--line);padding:10px;text-align:left;vertical-align:top}}th{{background:var(--paper)}}td ul{{padding-left:20px;margin:5px 0 10px}}td ul:last-child{{margin-bottom:0}}blockquote{{margin:16px 0;border-left:3px solid var(--line);padding:8px 14px;color:var(--muted)}}
.progress{{display:flex;flex-wrap:wrap;gap:12px 24px;padding-bottom:15px;border-bottom:1px solid var(--line);font-size:13px;font-variant-numeric:tabular-nums}}.progress b{{font-size:20px;color:var(--accent);margin-right:4px}}.status{{display:inline-block;white-space:nowrap;font-size:11px;line-height:1.5;padding:2px 6px;border:1px solid var(--line);border-radius:3px;font-weight:500;vertical-align:middle}}.status.open{{background:var(--soft);color:var(--accent)}}.status.confirmation{{background:var(--pink-soft);color:var(--pink)}}.status.answered{{background:var(--green-soft);color:var(--green)}}.question-icon{{display:inline-flex;align-items:center;justify-content:center;border:1.5px solid var(--accent);border-radius:50%;width:21px;height:21px;margin-right:7px;color:var(--accent);font-size:14px;vertical-align:middle}}.note{{font-size:12px;color:var(--muted);margin:12px 0 24px}}
{preview_css}
@media(max-width:850px){{.layout{{display:block;padding:12px}}nav{{position:static;max-height:none;margin-bottom:20px}}nav>ul{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px}}main{{padding:20px}}}}@media(max-width:480px){{nav>ul{{display:block}}table{{min-width:420px}}h1{{font-size:24px}}}}@media print{{nav{{display:none}}.layout{{display:block;padding:0}}main{{border:0}}body{{background:white}}}}
</style></head><body><div class="layout"><nav aria-label="Question progress"><h2>Questions</h2><ul>{''.join(navigation)}</ul><ul class="sections">{sections}</ul></nav><main>
<div class="progress" aria-label="Question counts">{summary}</div><p class="note">All questions and options are shown below. Progress comes from recorded answers and verification; it is not design approval. Add feedback in your review tool.</p>
{body}
</main></div></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--title")
    args = parser.parse_args()
    try:
        page = render_html(args.source.read_text(encoding="utf-8"), title=args.title)
        args.html.write_text(page, encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
