"""Dependency-free validation for the JSON Schema subset used by SDLC state files."""

from __future__ import annotations

import re
from typing import Any


def _type_matches(value: object, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "null": value is None,
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }.get(expected, False)


def _resolve_ref(root: dict[str, Any], reference: str) -> dict[str, Any] | None:
    if not reference.startswith("#/"):
        return None
    current: object = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current if isinstance(current, dict) else None


def validate_schema_instance(instance: object, schema: dict[str, Any]) -> list[str]:
    """Return path-qualified errors for the supported draft-2020-12 keywords."""

    errors: list[str] = []

    def walk(value: object, rule: dict[str, Any], path: str) -> None:
        if "$ref" in rule:
            resolved = _resolve_ref(schema, str(rule["$ref"]))
            if resolved is None:
                errors.append(f"{path}: unresolved schema reference {rule['$ref']}")
                return
            walk(value, resolved, path)
            return

        if "oneOf" in rule:
            branch_errors: list[list[str]] = []
            for branch in rule["oneOf"]:
                before = len(errors)
                walk(value, branch, path)
                branch_errors.append(errors[before:])
                del errors[before:]
            matches = sum(not item for item in branch_errors)
            if matches != 1:
                errors.append(f"{path}: must match exactly one schema alternative")
            return

        expected = rule.get("type")
        if expected is not None:
            expected_types = expected if isinstance(expected, list) else [expected]
            if not any(_type_matches(value, item) for item in expected_types):
                errors.append(f"{path}: expected {' or '.join(expected_types)}")
                return

        if "const" in rule and value != rule["const"]:
            errors.append(f"{path}: must equal {rule['const']!r}")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{path}: value is not in the allowed enum")

        if isinstance(value, str):
            if "minLength" in rule and len(value) < rule["minLength"]:
                errors.append(f"{path}: string is shorter than {rule['minLength']}")
            if "pattern" in rule and re.search(rule["pattern"], value) is None:
                errors.append(f"{path}: does not match required pattern")

        if isinstance(value, list):
            if "minItems" in rule and len(value) < rule["minItems"]:
                errors.append(f"{path}: needs at least {rule['minItems']} item(s)")
            item_rule = rule.get("items")
            if isinstance(item_rule, dict):
                for index, item in enumerate(value):
                    walk(item, item_rule, f"{path}[{index}]")

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in rule and value < rule["minimum"]:
                errors.append(f"{path}: must be at least {rule['minimum']}")

        if isinstance(value, dict):
            required = rule.get("required", [])
            for key in required:
                if key not in value:
                    errors.append(f"{path}.{key}: required field is missing")
            properties = rule.get("properties", {})
            if rule.get("additionalProperties") is False:
                for key in sorted(set(value) - set(properties)):
                    errors.append(f"{path}.{key}: unknown field")
            for key, child_rule in properties.items():
                if key in value and isinstance(child_rule, dict):
                    walk(value[key], child_rule, f"{path}.{key}")

    walk(instance, schema, "$")
    return errors
