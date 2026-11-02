"""Trusted computation behind the common ZOOMCYCLE_CODE entry point.

This module knows no LENS names or LENS kinds. A binding selects an approved
algorithm implementation; every implementation receives the same validated
number-list input. The registry contains implementations, not LENS-specific
rules. Adding a LENS never requires editing this file.

Authentication, current-LENS checks, HASH ownership, and durable result/event
recording belong to the ZOOMBAR gateway. ``evaluate`` is its computation helper,
not an alternative public route into another LENS.

The explicit guards below validate untrusted input. They are deliberately not
disguised as boolean indexing or external tables of per-LENS exceptions.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Callable
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


Number = int | float
Numbers = tuple[Number, ...]

MAX_ITEMS = 100_000
MAX_LABEL_LENGTH = 256

_CYCLE_KEYS = (
    "BASE_PIN",
    "COMMON_ACTION",
    "INNER_LENS",
    "UNIQUE_ACTION",
)
_REQUEST_FIELDS = frozenset((*_CYCLE_KEYS, "data"))
_BINDING_REQUIRED = frozenset((*_CYCLE_KEYS, "algorithm"))
_BINDING_OPTIONAL = frozenset(("version", "input_type"))


class ExecutionError(ValueError):
    """A stable, serializable execution failure with no partial result."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True, slots=True)
class _Algorithm:
    implementation: Callable[[Numbers], Number]
    minimum_items: int = 0


def _average(values: Numbers) -> Number:
    # statistics.mean uses an exact internal sum, avoiding an intermediate
    # overflow for inputs such as [1e308, 1e308] whose mean is still finite.
    return statistics.mean(values)


# This immutable allowlist contains trusted functions, not code received through
# TYPE, HASH, a URL, or a request. There is no eval, dynamic import, or unrestricted
# getattr. ``kind`` and individual LENS identities play no part in resolution.
_ALGORITHMS = MappingProxyType(
    {
        "total": _Algorithm(sum),
        "count": _Algorithm(len),
        "average": _Algorithm(_average, minimum_items=1),
        "min": _Algorithm(min, minimum_items=1),
        "max": _Algorithm(max, minimum_items=1),
    }
)


def approved_algorithms() -> tuple[str, ...]:
    """Return the stable catalog of implemented, approved operations."""
    return tuple(sorted(_ALGORITHMS))


def _fields(
    value: Any,
    required: frozenset[str],
    optional: frozenset[str],
    code: str,
) -> dict[str, Any]:
    if type(value) is not dict:
        raise ExecutionError(code, "An ordinary JSON object is required.")
    if not all(type(key) is str for key in value):
        raise ExecutionError(code, "Object keys must be strings.")
    missing = required.difference(value)
    unknown = value.keys() - required - optional
    if missing:
        raise ExecutionError(code, "Missing fields: " + ", ".join(sorted(missing)))
    if unknown:
        raise ExecutionError(code, "Unknown fields: " + ", ".join(sorted(unknown)))
    return value


def _label(value: Any, field: str) -> str:
    if type(value) is not str:
        raise ExecutionError("BAD_BINDING", f"{field} must be a string.")
    if not value.strip() or len(value) > MAX_LABEL_LENGTH or "\0" in value:
        raise ExecutionError("BAD_BINDING", f"{field} is empty or exceeds its limits.")
    return value


def validate_binding(binding: dict[str, Any]) -> dict[str, Any]:
    """Validate and copy an external, JSON-serializable action descriptor.

    Bindings are persisted by the gateway under its privileged configuration
    boundary. This routine neither installs code nor grants permission.
    """
    binding = _fields(
        binding, _BINDING_REQUIRED, _BINDING_OPTIONAL, "BAD_BINDING"
    )
    normalized = {key: _label(binding[key], key) for key in _CYCLE_KEYS}
    algorithm = _label(binding["algorithm"], "algorithm")
    if algorithm not in _ALGORITHMS:
        raise ExecutionError("UNAPPROVED_ALGORITHM", "Algorithm is not approved.")
    version = binding.get("version", 1)
    if type(version) is not int or not 1 <= version <= 2**31 - 1:
        raise ExecutionError("BAD_BINDING", "version must be a positive 32-bit integer.")
    input_type = binding.get("input_type", "number_list")
    if input_type != "number_list" or type(input_type) is not str:
        raise ExecutionError("BAD_BINDING", "Unsupported input contract.")
    normalized.update(
        version=version, algorithm=algorithm, input_type=input_type
    )
    return normalized


def _finite(value: Any) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _numbers(value: Any, minimum_items: int) -> Numbers:
    if type(value) is not list:
        raise ExecutionError("BAD_INPUT_TYPE", "data must be a JSON number list.")
    if len(value) > MAX_ITEMS:
        raise ExecutionError("INPUT_LIMIT", f"data exceeds {MAX_ITEMS} items.")
    if len(value) < minimum_items:
        raise ExecutionError("INPUT_EMPTY", "This operation needs at least one number.")
    if not all(_finite(item) for item in value):
        raise ExecutionError("BAD_NUMBER", "All items must be finite numbers; booleans are rejected.")
    return tuple(value)


def evaluate(request: dict[str, Any], binding: dict[str, Any]) -> Number:
    """Run one validated action without reading or modifying any LENS state.

    All four selection fields must equal the installed contract. The caller
    must already have authenticated the session, proved that INNER_LENS is the
    current LENS, resolved the PARAMETER_HASH in that LENS, and checked execution
    permission. The caller records the returned value as data/HASH plus an
    event; ZOOMCYCLE_CODE itself does not return a business value to the client.

    Lists are numeric data, never boolean-indexed dispatch instructions. Empty
    inputs are valid for total/count, and invalid for average/min/max.
    """
    descriptor = validate_binding(binding)
    request = _fields(request, _REQUEST_FIELDS, frozenset(), "REQUEST_FIELDS")
    choices = {key: request[key] for key in _CYCLE_KEYS}
    expected = {key: descriptor[key] for key in _CYCLE_KEYS}
    if choices != expected:
        raise ExecutionError("CONTRACT_MISMATCH", "Request does not match the installed action contract.")
    algorithm = _ALGORITHMS[descriptor["algorithm"]]
    values = _numbers(request["data"], algorithm.minimum_items)
    try:
        result = algorithm.implementation(values)
    except ArithmeticError as exc:
        raise ExecutionError("ARITHMETIC_ERROR", "The operation exceeded the numeric domain.") from exc
    if not _finite(result):
        raise ExecutionError("RESULT_NOT_FINITE", "The operation did not produce a finite JSON number.")
    return result
