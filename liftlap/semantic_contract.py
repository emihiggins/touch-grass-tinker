"""Pure, typed semantic validation for extracted intent.

The v2 intent shape remains the historical wire format. The opt-in envelope
adds provenance without changing that shape, so old artifacts and scores remain
readable. This module deliberately does not inspect request prose.
"""
from dataclasses import dataclass
from typing import Any

from scripts.benchmark import FIELDS_V2, REQUIRED, validate_intent

CONTRACT_VERSION = 1
PROVENANCE = {"user", "context", "missing"}
PROVENANCE_FIELDS = FIELDS_V2 - {"schema_version"}


@dataclass(frozen=True)
class SemanticIssue:
    code: str
    path: str
    message: str

    def as_dict(self):
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class SemanticResult:
    valid: bool
    intent: dict[str, Any] | None
    issues: tuple[SemanticIssue, ...]
    contract_version: int | None

    @property
    def plan_allowed(self):
        return self.valid and self.intent is not None and self.intent.get("status") == "ready"

    def as_dict(self):
        return {"valid": self.valid, "plan_allowed": self.plan_allowed,
                "contract_version": self.contract_version,
                "issues": [issue.as_dict() for issue in self.issues]}


def _issue(code, path, message):
    return SemanticIssue(code, path, message)


def _check_shape(intent, place_ids):
    try:
        validate_intent(intent, place_ids)
        return []
    except (ValueError, TypeError, KeyError) as error:
        text = str(error)
        code = {"Invalid schema version": "unsupported_contract",
                "Ready intent incomplete": "ready_missing_required",
                "Clarification fields required": "clarification_without_field",
                "Invalid or conflicting soft lift preferences": "conflicting_lift_constraints"}.get(text, "schema_invalid")
        return [_issue(code, "intent", text)]


def _semantic_checks(intent):
    issues = []
    if intent.get("status") == "ready" and intent.get("clarification_fields"):
        issues.append(_issue("ready_with_clarification", "intent.clarification_fields", "Ready intent cannot retain clarification fields"))
    if intent.get("status") == "ready" and intent.get("hard_max_difficulty") is None:
        issues.append(_issue("unknown_difficulty", "intent.hard_max_difficulty", "Maximum difficulty is explicitly unknown; planning is blocked"))
    hard = set(intent.get("excluded_lift_types", []))
    soft = set(intent.get("avoided_lift_types", []))
    if hard & soft:
        issues.append(_issue("conflicting_lift_constraints", "intent.avoided_lift_types", "A hard exclusion cannot also be a soft preference"))
    return issues


def validate_intent_semantics(intent, place_ids, *, contract_version=None):
    """Validate a bare legacy/v2 intent and return structured issues."""
    issues = _check_shape(intent, place_ids)
    if not issues:
        issues.extend(_semantic_checks(intent))
    return SemanticResult(not issues, intent if not issues else None, tuple(issues), contract_version)


def resolve_extraction(envelope, context, place_ids):
    """Resolve an opt-in provenance envelope; context never overrides user data.

    explicit_unknown is authoritative and prevents a UI default from filling a
    field the user/model marked unknown. No request-text inference occurs here.
    """
    issues = []
    if not isinstance(envelope, dict) or envelope.get("contract_version") != CONTRACT_VERSION:
        return SemanticResult(False, None, (_issue("unsupported_contract", "contract_version", "Opt-in extraction contract version is required"),), None)
    intent = envelope.get("intent")
    provenance = envelope.get("provenance")
    explicit_unknown = envelope.get("explicit_unknown", [])
    if not isinstance(intent, dict) or not isinstance(provenance, dict) or not isinstance(explicit_unknown, list):
        return SemanticResult(False, None, (_issue("malformed_envelope", "", "Envelope requires intent, provenance, and explicit_unknown"),), CONTRACT_VERSION)
    if set(provenance) - PROVENANCE_FIELDS or any(v not in PROVENANCE for v in provenance.values()):
        issues.append(_issue("invalid_provenance", "provenance", "Every provenance value must be user, context, or missing"))
    if set(explicit_unknown) - PROVENANCE_FIELDS:
        issues.append(_issue("unknown_field", "explicit_unknown", "Unknown fields cannot be marked explicitly"))
    resolved = dict(intent)
    for field, source in provenance.items():
        if source == "context" and field in context and field not in explicit_unknown and resolved.get(field) is None:
            resolved[field] = context[field]
        if source == "missing" and field not in explicit_unknown:
            issues.append(_issue("missing_provenance", f"provenance.{field}", "Missing values require an explicit unknown marker"))
    for field in explicit_unknown:
        resolved[field] = None
        if field in REQUIRED:
            resolved.setdefault("clarification_fields", [])
            resolved["clarification_fields"] = sorted(set(resolved["clarification_fields"]) | {field})
    if issues:
        return SemanticResult(False, None, tuple(issues), CONTRACT_VERSION)
    return validate_intent_semantics(resolved, place_ids, contract_version=CONTRACT_VERSION)
