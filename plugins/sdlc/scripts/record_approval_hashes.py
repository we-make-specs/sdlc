#!/usr/bin/env python3
"""Record approval hashes and regenerate the exact human views atomically."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_decision_manifest import (
    active_scope_errors,
    approval_header_errors,
    decision_content_hash,
    validate_decision_manifest,
)
from render_decision_gate import render_html as render_gate_html, render_markdown as render_gate_markdown
from render_target_solution import render_html as render_target_html


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content.encode("utf-8"))
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
    target_view = artifact_dir / "03-target-solution.view.html"
    sources = {
        "agreement": (artifact_dir / "03-agreement.spec.md").read_bytes(),
        "targetSolution": (artifact_dir / "03-target-solution.spec.md").read_bytes(),
        "testScenarios": (artifact_dir / "03-test-scenarios.spec.md").read_bytes(),
    }
    errors = active_scope_errors(data)
    for key, name in (("targetSolution", "03-target-solution.spec.md"), ("testScenarios", "03-test-scenarios.spec.md")):
        errors.extend(approval_header_errors(approval, sources[key].decode("utf-8"), name))
    if errors:
        raise ValueError("; ".join(errors))

    data["activeSemanticChangeIds"] = []
    target_html = render_target_html(sources["targetSolution"].decode("utf-8"))
    hashes = {
        **{name: hashlib.sha256(content).hexdigest() for name, content in sources.items()},
        "targetSolutionView": hashlib.sha256(target_html.encode("utf-8")).hexdigest(),
        "decisionContent": decision_content_hash(data),
    }
    approval["artifactHashes"] = hashes
    errors = validate_decision_manifest(data, "approved", artifact_dir=None)
    if errors:
        raise ValueError("; ".join(errors))
    gate_markdown = render_gate_markdown(data, "alignment")
    gate_html = render_gate_html(data, "alignment")
    atomic_write(target_view, target_html)
    atomic_write(manifest_path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    atomic_write(artifact_dir / "03-human-decision-gate.view.md", gate_markdown)
    atomic_write(artifact_dir / "03-human-decision-gate.view.html", gate_html)
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
