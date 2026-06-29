"""Decision Framework runtime skeleton tests."""

from dataclasses import asdict, fields

from agent.decision_framework import (
    DecisionFrameworkInput,
    DecisionFrameworkOutput,
    run_decision_framework,
)


OUTPUT_FIELDS = {
    "perspective",
    "decision_synthesis",
    "next_step",
    "review_point",
}

INPUT_FIELDS = {
    "identity",
    "energy",
    "habit",
    "growth",
    "communication",
    "coaching",
}

FORBIDDEN_FIELDS = {
    "decision",
    "final_decision",
    "recommendation",
    "domain_decision",
    "domain",
    "domain_model",
    "investment",
    "career",
    "health",
    "business",
    "finance",
    "decision_style",
    "human_model_update",
}


def test_empty_mapping_input_returns_decision_framework_output():
    output = run_decision_framework({})

    assert isinstance(output, DecisionFrameworkOutput)
    assert asdict(output) == {
        "perspective": "",
        "decision_synthesis": {
            "options": [],
            "tradeoffs": [],
            "constraints": [],
            "unknowns": [],
        },
        "next_step": "",
        "review_point": "",
    }


def test_empty_dataclass_input_returns_decision_framework_output():
    output = run_decision_framework(DecisionFrameworkInput())

    assert isinstance(output, DecisionFrameworkOutput)


def test_input_contract_is_limited_to_six_human_model_fields():
    assert {field.name for field in fields(DecisionFrameworkInput)} == INPUT_FIELDS
    assert not ({field.name for field in fields(DecisionFrameworkInput)} & FORBIDDEN_FIELDS)


def test_mapping_input_accepts_six_human_model_fields_and_ignores_unknown_keys():
    input_data = {
        "identity": {"values": ["autonomy"]},
        "energy": {"level": "low"},
        "habit": {"shape": "small-step"},
        "growth": {"direction": "iterative"},
        "communication": {"style": "concise"},
        "coaching": {"stance": "supportive"},
        "decision_style": {"candidate": True},
        "unknown_key": {"ignored": True},
    }

    output = run_decision_framework(input_data)

    assert isinstance(output, DecisionFrameworkOutput)
    assert set(asdict(output)) == OUTPUT_FIELDS


def test_output_contract_is_limited_to_four_decision_support_fields():
    output = run_decision_framework({})

    assert {field.name for field in fields(DecisionFrameworkOutput)} == OUTPUT_FIELDS
    assert set(asdict(output)) == OUTPUT_FIELDS


def test_decision_synthesis_contract_contains_only_empty_lists():
    output = run_decision_framework({})

    assert set(output.decision_synthesis) == {
        "options",
        "tradeoffs",
        "constraints",
        "unknowns",
    }
    assert all(isinstance(value, list) for value in output.decision_synthesis.values())
    assert all(value == [] for value in output.decision_synthesis.values())


def test_output_does_not_include_decision_or_domain_specific_fields():
    output = run_decision_framework({})
    output_data = asdict(output)

    assert not (set(output_data) & FORBIDDEN_FIELDS)
    assert "decision" not in output_data
    assert "final_decision" not in output_data
    assert "recommendation" not in output_data


def test_decision_style_is_not_required_input():
    output = run_decision_framework(
        {
            "identity": {},
            "energy": {},
            "habit": {},
            "growth": {},
            "communication": {},
            "coaching": {},
        }
    )

    assert isinstance(output, DecisionFrameworkOutput)
