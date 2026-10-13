#!/usr/bin/env python3
"""Record approval hashes and regenerate the exact human views atomically."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_decision_manifest import decision_content_hash, sha256_file
from render_decision_gate import render_html as render_gate_html, render_markdown as render_gate_markdown
from render_target_solution import render_html as render_target_html


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def record_hashes(manifest_path: Path) -> dict[str, str]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    approval = data.get("approval")
    if not isinstance(approval, dict) or approval.get("status") != "APPROVED":
        raise ValueError("set approval.status to APPROVED before recording approval hashes")

    artifact_dir = manifest_path.parent
    target_source = artifact_dir / "03-target-solution.spec.md"
    target_view = artifact_dir / "03-target-solution.view.html"
    atomic_write(target_view, render_target_html(target_source.read_text(encoding="utf-8")))
    hashes = {
        "agreement": sha256_file(artifact_dir / "03-agreement.spec.md"),
        "targetSolution": sha256_file(target_source),
        "targetSolutionView": sha256_file(target_view),
        "testScenarios": sha256_file(artifact_dir / "03-test-scenarios.spec.md"),
        "decisionContent": decision_content_hash(data),
    }
    approval["artifactHashes"] = hashes
    atomic_write(manifest_path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    atomic_write(artifact_dir / "03-human-decision-gate.view.md", render_gate_markdown(data, "alignment"))
    atomic_write(artifact_dir / "03-human-decision-gate.view.html", render_gate_html(data, "alignment"))
    return hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        hashes = record_hashes(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"recorded approval hashes ({len(hashes)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
