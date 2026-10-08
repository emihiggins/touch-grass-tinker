"""Pure, typed semantic validation for extracted intent.

The v2 intent shape remains the historical wire format. The opt-in envelope
adds provenance without changing that shape, so old artifacts and scores remain
readable. This module deliberately does not inspect request prose.
"""
from dataclasses import dataclass
import copy
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
    if intent.get("status") == "clarify":
        for field in sorted(REQUIRED):
            if field in intent["clarification_fields"] and intent[field] is not None:
                issues.append(_issue("clarification_retains_value", f"intent.{field}", "Confirm or clear the value being clarified"))
            if intent[field] is None and field not in intent["clarification_fields"]:
                issues.append(_issue("missing_value_not_clarified", f"intent.{field}", "Missing required value must be clarified"))
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
    if (not isinstance(envelope, dict) or type(envelope.get("contract_version")) is not int
            or envelope["contract_version"] != CONTRACT_VERSION):
        return SemanticResult(False, None, (_issue("unsupported_contract", "contract_version", "Opt-in extraction contract version is required"),), None)
    if set(envelope) != {"contract_version", "intent", "provenance", "explicit_unknown"} or not isinstance(context, dict):
        return SemanticResult(False, None, (_issue("malformed_envelope", "", "Exact envelope fields and object context required"),), CONTRACT_VERSION)
    intent = envelope.get("intent")
    provenance = envelope.get("provenance")
    explicit_unknown = envelope.get("explicit_unknown", [])
    if not isinstance(intent, dict) or not isinstance(provenance, dict) or not isinstance(explicit_unknown, list):
        return SemanticResult(False, None, (_issue("malformed_envelope", "", "Envelope requires intent, provenance, and explicit_unknown"),), CONTRACT_VERSION)
    if set(provenance) - PROVENANCE_FIELDS or any(not isinstance(v, str) or v not in PROVENANCE for v in provenance.values()):
        issues.append(_issue("invalid_provenance", "provenance", "Every provenance value must be user, context, or missing"))
    if (any(not isinstance(v, str) for v in explicit_unknown)
            or len(set(explicit_unknown)) != len(explicit_unknown) or set(explicit_unknown) - REQUIRED):
        issues.append(_issue("unknown_field", "explicit_unknown", "Unknown fields cannot be marked explicitly"))
    if issues:
        return SemanticResult(False, None, tuple(issues), CONTRACT_VERSION)
    resolved = copy.deepcopy(intent)
    for field, source in provenance.items():
        if source == "context" and field in context and field not in explicit_unknown and resolved.get(field) is None:
            resolved[field] = context[field]
        if source == "context" and field not in explicit_unknown and (field not in context or resolved.get(field) != context[field]):
            issues.append(_issue("context_value_conflict", f"provenance.{field}", "Context-sourced value must match supplied context"))
        if source == "user" and resolved.get(field) is None and field not in explicit_unknown:
            issues.append(_issue("user_value_missing", f"provenance.{field}", "User-sourced values cannot be missing"))
        if source == "missing" and (field not in explicit_unknown or resolved.get(field) is not None):
            issues.append(_issue("missing_provenance", f"provenance.{field}", "Missing values require null and an explicit unknown marker"))
    for field in explicit_unknown:
        resolved[field] = None
        fields = resolved.get("clarification_fields")
        if not isinstance(fields, list) or any(not isinstance(v, str) for v in fields):
            issues.append(_issue("malformed_envelope", "intent.clarification_fields", "Clarification fields must be a string list"))
            continue
        resolved["clarification_fields"] = sorted(set(fields) | {field})
        if resolved.get("status") == "ready":
            resolved["status"] = "clarify"
    if issues:
        return SemanticResult(False, None, tuple(issues), CONTRACT_VERSION)
    return validate_intent_semantics(resolved, place_ids, contract_version=CONTRACT_VERSION)
