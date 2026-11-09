"""Render the Markdown used by human delivery artifacts."""

from __future__ import annotations

import html
import re
import shlex
from collections.abc import Callable, Iterator
from itertools import groupby
from urllib.parse import unquote, urlsplit


LIST_ITEM = re.compile(r"^( *)([-+*]|[0-9]{1,9}[.)])([ \t]+)(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
FENCE = re.compile(r"^(`{3,}(?!`)(?=[^`]*$)|~{3,})(.*)$")
REFERENCE = re.compile(r"(?:^|\s)ref(?:\s|=|$)")
SOURCE_PREVIEW_CSS = """
.source-preview{margin:1em 0;border:1px solid var(--line,#d0d5dd);border-radius:8px}
.source-preview figcaption{display:flex;flex-wrap:wrap;align-items:baseline;gap:.4em .8em;padding:.5em .75em;overflow-wrap:anywhere}
.source-preview pre{margin:0;border-radius:0 0 7px 7px}
"""


def safe_link(value: str) -> str | None:
    """Allow local relative links and explicit HTTP(S) links."""
    candidate = value.strip()
    if (
        not candidate
        or candidate.startswith("//")
        or "\\" in candidate
        or any(ord(char) < 32 for char in candidate)
    ):
        return None
    try:
        scheme = urlsplit(candidate).scheme.lower()
    except ValueError:
        return None
    if scheme and scheme not in {"http", "https"}:
        return None
    return candidate


def source_url(value: str, revision: str, path: str, start: int, end: int) -> str:
    candidate = safe_link(value)
    if not candidate or "?" in candidate or any(char.isspace() for char in candidate):
        raise ValueError("code reference URL must be an HTTPS blob link")
    parsed = urlsplit(candidate)
    parts = parsed.path.split("/", 5)
    fragments = {f"L{start}-L{end}"}
    if start == end:
        fragments.add(f"L{start}")
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or len(parts) != 6
        or any(part in {".", ".."} or not re.fullmatch(r"[A-Za-z0-9_.-]+", part) for part in parts[1:3])
        or parts[3] != "blob"
        or parts[4].lower() != revision.lower()
        or unquote(parts[5]) != path
        or parsed.fragment not in fragments
    ):
        raise ValueError("code reference URL must point to the same revision, path and lines")
    return candidate


def validate_source_path(path: str) -> None:
    path_parts = path.split("/")
    if (
        any(part in {"", ".", ".."} for part in path_parts)
        or ":" in path_parts[0]
        or "\\" in path
        or any(ord(char) < 32 or ord(char) == 127 for char in path)
    ):
        raise ValueError("code reference path must be relative to the source repository")


def source_line_range(lines: str) -> tuple[int, int]:
    match = re.fullmatch(r"([1-9][0-9]*)(?:-([1-9][0-9]*))?", lines)
    if not match:
        raise ValueError("code reference lines must be a positive line or range")
    start, end = int(match.group(1)), int(match.group(2) or match.group(1))
    if end < start:
        raise ValueError("code reference line range ends before it starts")
    return start, end


def reference_tokens(info: str) -> list[str] | None:
    if not REFERENCE.search(info):
        return None
    try:
        tokens = shlex.split(info)
    except ValueError as exc:
        raise ValueError(f"invalid code reference metadata: {exc}") from exc
    if not any(token == "ref" or token.startswith("ref=") for token in tokens):
        return None
    if "\\" in info:
        raise ValueError("code reference metadata cannot contain backslashes")
    return tokens


def source_preview(tokens: list[str], snippet: list[str], used_ids: set[str]) -> str:
    language, *attributes_in = tokens
    if not re.fullmatch(r"[A-Za-z0-9_+.#-]+", language):
        raise ValueError("code reference requires a language before its attributes")

    attributes = {}
    for token in attributes_in:
        key, sep, value = token.partition("=")
        if not sep or not value or key not in {"ref", "path", "lines", "revision", "url"} or key in attributes:
            raise ValueError("code reference metadata has an invalid or repeated attribute")
        attributes[key] = value
    if not {"ref", "path", "lines", "revision"} <= attributes.keys():
        raise ValueError("code reference requires ref, path, lines and revision")

    reference, path, lines, revision = (attributes[key] for key in ("ref", "path", "lines", "revision"))
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", reference):
        raise ValueError("invalid code reference ID")
    validate_source_path(path)
    if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        raise ValueError("code reference revision must be a full 40-character commit")
    start, end = source_line_range(lines)
    if end - start + 1 != len(snippet):
        raise ValueError("code reference snippet does not match its line range")

    anchor = f"ref-{reference}"
    if anchor in used_ids:
        raise ValueError(f"duplicate code reference ID {reference}")
    used_ids.add(anchor)
    link = ""
    if "url" in attributes:
        url = source_url(attributes["url"], revision, path, start, end)
        link = f'<a href="{html.escape(url, quote=True)}">Open source</a>'
    location = html.escape(f"{path}:{lines}")
    code = html.escape("\n".join(snippet))
    return (
        f'<figure class="source-preview" id="{anchor}">'
        f"<figcaption><strong>{reference}</strong> <code>{location}</code> "
        f'<code title="{revision}" aria-label="Revision {revision}">{revision[:8]}</code> {link}</figcaption>'
        f'<pre><code class="language-{language}">{code}</code></pre></figure>'
    )


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
    for index in reversed(range(len(tokens))):
        escaped = escaped.replace(f"\x00{index}\x00", tokens[index])
    return escaped


def table_cells(line: str) -> list[str]:
    cells = re.split(r"(?<!\\)\|", line.strip())
    if not cells[0]:
        cells.pop(0)
    if cells and not cells[-1]:
        cells.pop()
    return [cell.strip().replace(r"\|", "|") for cell in cells]


def table_cell_html(cell: str) -> str:
    parts = []
    start = 0
    for token in re.finditer(r"`[^`]+`|<br[ \t]*/?>", cell, re.IGNORECASE):
        if token.group().startswith("<"):
            parts.append(cell[start:token.start()].strip())
            start = token.end()
    parts.append(cell[start:].strip())
    if len(parts) == 1 or not any(part.startswith("- ") for part in parts):
        return "<br>".join(inline_markdown(part) for part in parts)

    rendered = []
    for is_list, group in groupby(parts, key=lambda part: part.startswith("- ")):
        if is_list:
            rendered.append("<ul>" + "".join(f"<li>{inline_markdown(part[2:])}</li>" for part in group) + "</ul>")
        else:
            rendered.extend(f"<p>{inline_markdown(part)}</p>" for part in group if part)
    return "".join(rendered)


def table_html(lines: list[str]) -> str:
    rows = [table_cells(line) for line in lines]
    if len(rows) > 1 and rows[1] and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in rows[1]):
        header, body = rows[0], rows[2:]
    else:
        header, body = rows[0], rows[1:]
    head = "".join(f"<th>{inline_markdown(cell)}</th>" for cell in header)
    rendered_rows = "".join(
        "<tr>" + "".join(f"<td>{table_cell_html(cell)}</td>" for cell in row) + "</tr>"
        for row in body
    )
    return f"<div class=table-wrap><table><thead><tr>{head}</tr></thead><tbody>{rendered_rows}</tbody></table></div>"


def fenced_code_end(lines: list[str], index: int, marker: str) -> int:
    closing = re.compile(re.escape(marker[0]) + f"{{{len(marker)},}}")
    index += 1
    while index < len(lines) and not closing.fullmatch(lines[index].strip()):
        index += 1
    return index


def list_items(lines: list[str], index: int) -> tuple[list[tuple[int, list[str]]], int, bool]:
    first = LIST_ITEM.match(lines[index])
    assert first
    indent = len(first.group(1))
    ordered = first.group(2)[0].isdigit()
    items: list[tuple[int, list[str]]] = []
    loose = False
    while index < len(lines):
        item = LIST_ITEM.match(lines[index])
        if not item or len(item.group(1)) != indent or item.group(2)[0].isdigit() != ordered:
            break
        content = [item.group(4)]
        content_indent = item.start(4)
        start = index
        index += 1
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                next_index = index + 1
                while next_index < len(lines) and not lines[next_index].strip():
                    next_index += 1
                if next_index == len(lines):
                    index = next_index
                    break
                next_line = lines[next_index]
                if len(next_line) - len(next_line.lstrip(" ")) <= indent:
                    next_item = LIST_ITEM.match(next_line)
                    if next_item and len(next_item.group(1)) == indent and next_item.group(2)[0].isdigit() == ordered:
                        loose = True
                    index = next_index
                    break
                content.extend(lines[index:next_index])
                index = next_index
                continue
            line_indent = len(line) - len(line.lstrip(" "))
            if line_indent <= indent:
                break
            content.append(line[min(content_indent, line_indent):])
            index += 1
        items.append((start, content))

    return items, index, loose


def markdown_content_lines(lines: list[str], offset: int = 0) -> Iterator[tuple[int, str]]:
    index = 0
    while index < len(lines):
        line = lines[index]
        fence = FENCE.match(line.strip())
        if fence:
            index = fenced_code_end(lines, index, fence.group(1)) + 1
        elif LIST_ITEM.match(line):
            items, index, _ = list_items(lines, index)
            for start, content in items:
                yield from markdown_content_lines(content, offset + start)
        else:
            yield offset + index, line
            index += 1


def list_html(lines: list[str], index: int, render_blocks: Callable[[list[str]], list[str]]) -> tuple[str, int]:
    first = LIST_ITEM.match(lines[index])
    assert first
    ordered = first.group(2)[0].isdigit()
    tag = "ol" if ordered else "ul"
    start = int(first.group(2)[:-1]) if ordered else 1
    opening = f'<ol start="{start}">' if start != 1 else f"<{tag}>"
    items, index, loose = list_items(lines, index)

    rendered = []
    for _, content in items:
        blocks = render_blocks(content)
        has_paragraph_break = any(not line.strip() for line in content)
        if not loose and not has_paragraph_break and blocks and blocks[0].startswith("<p>"):
            blocks[0] = blocks[0][3:-4]
        rendered.append("<li>" + "\n".join(blocks) + "</li>")
    return opening + "".join(rendered) + f"</{tag}>", index


def markdown_body(source: str, *, default_title: str = "Target solution") -> tuple[str, list[tuple[int, str, str]], str]:
    headings: list[tuple[int, str, str]] = []
    title = default_title
    used_slugs: set[str] = set()

    def render_blocks(lines: list[str]) -> list[str]:
        nonlocal title
        output: list[str] = []
        index = 0
        paragraph: list[str] = []

        def flush_paragraph() -> None:
            if paragraph:
                output.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
                paragraph.clear()

        while index < len(lines):
            line = lines[index]
            stripped = line.strip()
            if not stripped:
                flush_paragraph()
                index += 1
                continue

            fence = FENCE.match(stripped)
            if fence:
                flush_paragraph()
                marker, language = fence.group(1), fence.group(2).strip()
                start = index + 1
                index = fenced_code_end(lines, index, marker)
                snippet = lines[start:index]
                tokens = reference_tokens(language)
                if tokens is not None:
                    if index == len(lines):
                        raise ValueError("unclosed code reference fence")
                    output.append(source_preview(tokens, snippet, used_slugs))
                    index += 1
                    continue
                code = html.escape("\n".join(snippet))
                index += 1
                language_class = re.sub(r"[^a-zA-Z0-9_-]", "", language)
                label = f"<div class=code-label>{html.escape(language)}</div>" if language else ""
                output.append(f"<div class=code-block>{label}<pre><code class='language-{language_class}'>{code}</code></pre></div>")
                continue

            heading = HEADING.match(line)
            if heading:
                flush_paragraph()
                level = len(heading.group(1))
                heading_text = re.sub(r"[*_`]", "", heading.group(2)).strip()
                slug = slugify(heading_text, used_slugs)
                if level == 1 and title == default_title:
                    title = heading_text
                headings.append((level, heading_text, slug))
                output.append(f"<h{level} id='{slug}'>{inline_markdown(heading.group(2))}</h{level}>")
                index += 1
                continue

            if stripped.startswith("|") and "|" in stripped[1:]:
                flush_paragraph()
                start = index
                while index < len(lines) and lines[index].strip().startswith("|"):
                    index += 1
                output.append(table_html(lines[start:index]))
                continue

            if LIST_ITEM.match(line):
                flush_paragraph()
                rendered_list, index = list_html(lines, index, render_blocks)
                output.append(rendered_list)
                continue

            if stripped.startswith(">"):
                flush_paragraph()
                quote: list[str] = []
                while index < len(lines) and lines[index].strip().startswith(">"):
                    quote.append(lines[index].strip().lstrip(">").strip())
                    index += 1
                output.append(f"<blockquote>{inline_markdown(' '.join(quote))}</blockquote>")
                continue

            paragraph.append(stripped)
            index += 1

        flush_paragraph()
        return output

    body = render_blocks(source.replace("\r\n", "\n").split("\n"))
    return "\n".join(body), headings, title
