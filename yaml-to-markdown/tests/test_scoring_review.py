import copy
import sys
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_DIR))

from scoring_review import (  # noqa: E402
    PROJECT_DIR,
    generated_documents,
    load_yaml,
    render_impact,
    validate_definition,
)


def definition(scores):
    return {
        "title": "Test score",
        "description": "Test definition",
        "version": "1.0.0",
        "scores": scores,
    }


def leaf(value=1, conditions=None):
    requirement = {"value": value, "description": "A requirement", "query": "ASK { ?iri ?p ?o }"}
    if conditions:
        requirement["conditions"] = conditions
    return {"title": "Leaf", "description": "Leaf score", "requirements": [requirement]}


class ValidationTests(unittest.TestCase):
    def test_repository_definitions_are_valid(self):
        for path in sorted((PROJECT_DIR / "definitions").glob("*.yaml")):
            self.assertEqual([], validate_definition(load_yaml(path), path.name))

    def test_missing_reference_is_rejected(self):
        data = definition({"a1": leaf(conditions=[{"key": "missing", "value": "max", "title": "Missing"}])})
        self.assertTrue(any("missing score 'missing'" in error for error in validate_definition(data)))

    def test_impossible_threshold_is_rejected(self):
        data = definition(
            {
                "a1": leaf(1),
                "a2": leaf(conditions=[{"key": "a1", "value": 2, "title": "Impossible"}]),
            }
        )
        self.assertTrue(any("threshold 2 exceeds 'a1' maximum 1" in error for error in validate_definition(data)))

    def test_circular_dependency_is_rejected(self):
        data = definition(
            {
                "a1": leaf(conditions=[{"key": "a2", "value": "max", "title": "A2"}]),
                "a2": leaf(conditions=[{"key": "a1", "value": "max", "title": "A1"}]),
            }
        )
        self.assertTrue(any("circular dependency" in error for error in validate_definition(data)))


class OutputTests(unittest.TestCase):
    def test_generated_documents_match_expected_file_set(self):
        paths = {path.relative_to(PROJECT_DIR).as_posix() for path in generated_documents()}
        self.assertEqual(
            {
                "docs/README.md",
                "docs/care-dependencies.md",
                "docs/care-scoring.md",
                "docs/fair-dependencies.md",
                "docs/fair-scoring.md",
            },
            paths,
        )

    def test_impact_reports_maximum_and_transitive_dependants(self):
        base = definition(
            {
                "a1": leaf(1),
                "a2": {
                    **leaf(1),
                    "prerequisites": {"conditions": [{"key": "a1", "value": "max", "title": "A1"}]},
                },
                "a3": {
                    **leaf(1),
                    "prerequisites": {"conditions": [{"key": "a2", "value": "max", "title": "A2"}]},
                },
            }
        )
        current = copy.deepcopy(base)
        current["scores"]["a1"]["requirements"].append(
            {"value": 1, "description": "New requirement", "query": "ASK { ?iri ?p ?o }"}
        )
        report = render_impact(current, base, "test")
        self.assertIn("| A1 | 1 | 0 | 0 |", report)
        self.assertIn("A1 added: New requirement", report)
        self.assertIn("| A1 | 1 | 2 |", report)
        self.assertIn("A1 → A2, A3", report)


if __name__ == "__main__":
    unittest.main()
