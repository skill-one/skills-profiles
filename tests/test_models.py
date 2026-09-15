"""Tests for the ImagePrompt schema: every rejection rule is enforced here,
so the cover.md prompt only has to teach them once and instructor retries
correct the rest before a bad recipe is ever stored."""

import pytest
from pydantic import ValidationError

from skills_profiles.models import ImagePrompt


def test_accepts_a_conforming_recipe():
    prompt = ImagePrompt(text="one brass compass, slim legs, rounded hinge")
    assert prompt.text == "one brass compass, slim legs, rounded hinge"


def test_normalizes_whitespace_and_trailing_punctuation():
    prompt = ImagePrompt(text="  one  small  stapler,  red body,; ")
    assert prompt.text == "one small stapler, red body"


def test_rejects_non_ascii():
    with pytest.raises(ValidationError, match="纯英文"):
        ImagePrompt(text="one 个订书机, red body")


def test_rejects_a_missing_one_prefix():
    with pytest.raises(ValidationError, match="one "):
        ImagePrompt(text="a round magnifying glass, brass rim, clear lens")


@pytest.mark.parametrize("text", [
    "one " + "long " * 41 + "phrase",
    "",
])
def test_rejects_overlong_or_empty(text):
    with pytest.raises(ValidationError):
        ImagePrompt(text=text)


def test_rejects_sentence_punctuation():
    with pytest.raises(ValidationError, match="逗号分隔"):
        ImagePrompt(text="one stapler, a really good one!")
