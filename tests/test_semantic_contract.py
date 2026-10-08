import copy
import unittest

from liftlap.fixtures import graph, scenario
from liftlap.rules import interpret
from liftlap.semantic_contract import CONTRACT_VERSION, resolve_extraction, validate_intent_semantics
from liftlap.server import context, handle_api


class SemanticContractTests(unittest.TestCase):
    def setUp(self):
        self.g, self.ui, self.catalog = context("synthetic")
        self.base = interpret("", self.ui, self.catalog, schema_version=2)["intent"]

    def envelope(self, intent=None, provenance=None, unknown=None, context_values=None):
        return {
            "contract_version": CONTRACT_VERSION,
            "intent": copy.deepcopy(intent or self.base),
            "provenance": provenance or {},
            "explicit_unknown": unknown or [],
        }, context_values or {}

    def test_invalid_semantics_are_typed_and_block_planning(self):
        invalid = copy.deepcopy(self.base)
        invalid["status"] = "ready"
        invalid["hard_max_difficulty"] = None
        result = validate_intent_semantics(invalid, {"base", "summit", "mid"})
        self.assertFalse(result.valid)
        self.assertFalse(result.plan_allowed)
        self.assertEqual(result.issues[0].code, "ready_missing_required")
        with self.assertRaisesRegex(ValueError, "ready_missing_required"):
            handle_api("/api/plan", {"intent": invalid})

    def test_valid_but_infeasible_is_not_invalid(self):
        intent = interpret("1 minute", self.ui, self.catalog, schema_version=2)["intent"]
        result = validate_intent_semantics(intent, {"base", "summit", "mid"})
        self.assertTrue(result.valid)
        planned = handle_api("/api/plan", {"intent": intent})
        self.assertEqual(planned["status"], "no_route")

    def test_user_value_precedes_context_default(self):
        intent = copy.deepcopy(self.base)
        intent["duration_minutes"] = 10
        envelope, ctx = self.envelope(intent, {"duration_minutes": "user"}, context_values={"duration_minutes": 60})
        result = resolve_extraction(envelope, ctx, {"base", "summit", "mid"})
        self.assertTrue(result.valid)
        self.assertEqual(result.intent["duration_minutes"], 10)

    def test_context_fills_only_missing_opt_in_field(self):
        intent = copy.deepcopy(self.base)
        intent["duration_minutes"] = None
        intent["status"] = "clarify"
        intent["clarification_fields"] = ["duration_minutes"]
        envelope, ctx = self.envelope(intent, {"duration_minutes": "context"}, context_values={"duration_minutes": 60})
        result = resolve_extraction(envelope, ctx, {"base", "summit", "mid"})
        self.assertTrue(result.valid)
        self.assertEqual(result.intent["duration_minutes"], 60)

    def test_explicit_unknown_cannot_be_filled_by_context(self):
        intent = copy.deepcopy(self.base)
        intent["duration_minutes"] = None
        intent["status"] = "clarify"
        intent["clarification_fields"] = ["duration_minutes"]
        envelope, ctx = self.envelope(intent, {"duration_minutes": "context"}, ["duration_minutes"], {"duration_minutes": 60})
        result = resolve_extraction(envelope, ctx, {"base", "summit", "mid"})
        self.assertTrue(result.valid)
        self.assertFalse(result.plan_allowed)
        self.assertEqual(result.intent["duration_minutes"], None)

    def test_legacy_v2_remains_valid_without_provenance(self):
        result = validate_intent_semantics(self.base, {"base", "summit", "mid"})
        self.assertTrue(result.valid)
        self.assertIsNone(result.contract_version)


if __name__ == "__main__":
    unittest.main()
