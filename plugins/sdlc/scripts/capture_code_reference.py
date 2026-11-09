#!/usr/bin/env python3
"""Print a Markdown code reference from a local Git commit."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
from pathlib import Path
from urllib.parse import quote

from artifact_view import source_line_range, source_preview, validate_source_path


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(repo), *args],
        capture_output=True,
        check=True,
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
    )
    return result.stdout.decode("utf-8")


def capture_reference(
    repo: Path,
    reference: str,
    path: str,
    lines: str,
    revision: str,
    language: str,
    repository_url: str | None = None,
) -> str:
    validate_source_path(path)
    start, end = source_line_range(lines)
    commit = git(repo, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}").strip()
    content = git(repo, "cat-file", "blob", f"{commit}:{path}")
    if "\0" in content:
        raise ValueError("code reference source must be text")
    file_lines = content.replace("\r\n", "\n").split("\n")
    if file_lines[-1] == "":
        file_lines.pop()
    if end > len(file_lines):
        raise ValueError(f"line {end} is outside {path} at {commit}")
    snippet = file_lines[start - 1:end]

    attributes = [language, f"ref={reference}", f"path={path}", f"lines={lines}", f"revision={commit}"]
    if repository_url:
        anchor = f"L{start}" if start == end else f"L{start}-L{end}"
        upstream = repository_url.rstrip("/").removesuffix(".git")
        url = f"{upstream}/blob/{commit}/{quote(path, safe='/')}#{anchor}"
        attributes.append(f"url={url}")

    source_preview(attributes, snippet, set())
    info = shlex.join(attributes)
    marker = "~" if "`" in info else "`"
    closing_lengths = [len(line.strip()) for line in snippet if re.fullmatch(re.escape(marker) + "+", line.strip())]
    fence = marker * max(3, max(closing_lengths, default=2) + 1)
    return "\n".join([f"{fence}{info}", *snippet, fence, ""])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Local Git checkout")
    parser.add_argument("--ref", required=True, help="Artifact reference ID")
    parser.add_argument("--path", required=True, help="File path relative to the repository")
    parser.add_argument("--lines", required=True, help="One-based line or inclusive range")
    parser.add_argument("--revision", required=True, help="Local Git revision to resolve")
    parser.add_argument("--language", required=True, help="Markdown code language")
    parser.add_argument("--repository-url", help="Verified HTTPS URL of the source repository")
    args = parser.parse_args()
    try:
        block = capture_reference(args.repo, args.ref, args.path, args.lines, args.revision, args.language, args.repository_url)
    except subprocess.CalledProcessError as exc:
        parser.error(exc.stderr.decode("utf-8", errors="replace").strip() or "Git lookup failed")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(block, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
