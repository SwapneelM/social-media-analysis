"""Tests for claims.prompts module."""

from claims.prompts import build_extraction_prompt, SYSTEM_PROMPT, FEW_SHOT_EXAMPLES


def test_system_prompt_exists():
    """System prompt should be a non-empty string."""
    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 100


def test_system_prompt_mentions_factual_claims():
    """System prompt should instruct about factual claims extraction."""
    assert "factual claim" in SYSTEM_PROMPT.lower()


def test_system_prompt_mentions_json():
    """System prompt should mention JSON output format."""
    assert "JSON" in SYSTEM_PROMPT


def test_few_shot_examples_exist():
    """Few-shot examples should be a non-empty list."""
    assert isinstance(FEW_SHOT_EXAMPLES, list)
    assert len(FEW_SHOT_EXAMPLES) >= 4  # At least 2 pairs (user + assistant)


def test_few_shot_examples_alternate_roles():
    """Few-shot examples should alternate between user and assistant."""
    for i in range(0, len(FEW_SHOT_EXAMPLES), 2):
        assert FEW_SHOT_EXAMPLES[i]["role"] == "user"
        assert FEW_SHOT_EXAMPLES[i + 1]["role"] == "assistant"


def test_few_shot_includes_no_claims_example():
    """Few-shot examples should include a case with no claims."""
    for ex in FEW_SHOT_EXAMPLES:
        if ex["role"] == "assistant" and '"claims": []' in ex["content"]:
            return
    assert False, "No 'empty claims' example found in few-shot examples"


def test_build_extraction_prompt_structure():
    """build_extraction_prompt should return properly structured messages."""
    messages = build_extraction_prompt("Test post about AI.")
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert messages[-1]["role"] == "user"
    assert "Test post about AI." in messages[-1]["content"]


def test_build_extraction_prompt_includes_few_shot():
    """build_extraction_prompt should include few-shot examples."""
    messages = build_extraction_prompt("Test post")
    # System prompt + few-shot examples + user message
    expected_len = 1 + len(FEW_SHOT_EXAMPLES) + 1
    assert len(messages) == expected_len


def test_build_extraction_prompt_wraps_text():
    """build_extraction_prompt should wrap post text in the user message."""
    messages = build_extraction_prompt("Some specific post text here")
    assert "Some specific post text here" in messages[-1]["content"]
    assert "Analyze this social media post" in messages[-1]["content"]
