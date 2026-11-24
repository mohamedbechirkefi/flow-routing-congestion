# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Versioned JSON result schema: validation at export and at import (fail closed).

The schema lives in ``schemas/result-1.0.0.json`` (JSON Schema 2020-12 syntax).
This module implements the subset of keywords the schema uses, so validation
needs no extra dependency: type, enum, required, properties,
additionalProperties (false), items, minimum. Non-finite numbers are rejected.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

SCHEMA_VERSION = "flow.result/1.0.0"
SCHEMA_PATH = Path(__file__).with_name("schemas") / "result-1.0.0.json"


class SchemaError(ValueError):
    """A result document does not match the versioned schema."""


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _check(value, schema: dict, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise SchemaError(f"{where}: non-finite number")
    t = schema.get("type")
    if t is not None:
        types = [t] if isinstance(t, str) else t
        if not any(_TYPES[x](value) for x in types):
            raise SchemaError(f"{where}: expected {types}, got {type(value).__name__}")
    if "enum" in schema and value not in schema["enum"]:
        raise SchemaError(f"{where}: {value!r} not in {schema['enum']}")
    if "minimum" in schema and isinstance(value, (int, float)) and value < schema["minimum"]:
        raise SchemaError(f"{where}: {value} < minimum {schema['minimum']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise SchemaError(f"{where}: missing required key {key!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(props)
            if extra:
                raise SchemaError(f"{where}: unexpected keys {sorted(extra)}")
        for key, sub in props.items():
            if key in value:
                _check(value[key], sub, f"{where}.{key}")
        # free-form objects (metrics, factors): still reject non-finite numbers
        for key, v in value.items():
            if key not in props:
                _check(v, {}, f"{where}.{key}")
    if isinstance(value, list):
        item_schema = schema.get("items", {})
        for i, v in enumerate(value):
            _check(v, item_schema, f"{where}[{i}]")


def validate_result(doc: dict) -> dict:
    """Raise SchemaError unless ``doc`` matches the result schema; return ``doc``."""
    _check(doc, load_schema(), "result")
    return doc


def clean_json(obj):
    """Convert NaN/inf to None and numpy scalars to Python types before export."""
    if isinstance(obj, dict):
        return {str(k): clean_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_json(v) for v in obj]
    if hasattr(obj, "item") and not isinstance(obj, (str, bytes)):
        obj = obj.item()
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj


def dump_result(doc: dict, path: Path) -> None:
    validate_result(doc)
    path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")


def load_result(path: Path) -> dict:
    try:
        doc = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaError(f"cannot read result file {path}: {exc}") from exc
    return validate_result(doc)
