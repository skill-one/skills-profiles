"""Tests for the markdown-file-backed prompt DAG."""

from pathlib import Path

import pytest

from skills_profiles.models import Domain, IntroText
from skills_profiles.prompts import _load_prompt, load_prompt_set, render_user_prompt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"


@pytest.fixture
def prompts():
    return load_prompt_set(PROMPTS_DIR)


class FakeSkill:
    id = "a/b/c"
    name = "Alpha"
    description = "Alpha 的技能描述"
    skill_md = "Alpha does useful things."


def test_all_prompts_loaded_from_files(prompts):
    expected = {"domain", "scenario", "blackbox", "whitebox",
                "tagline", "persona", "comments", "cover"}
    assert set(prompts.by_id) == expected
    files = {p.stem for p in PROMPTS_DIR.glob("*.md") if not p.name.startswith("_")}
    assert files == expected


def test_system_prompt_template_loaded(prompts):
    assert "推销自己" in prompts.system_template
    assert "{{ skill_md }}" in prompts.system_template


def test_system_prompt_renders_skill_context(prompts):
    """The rendered system prompt carries the skill's SKILL.md source."""
    system = prompts.render_system_prompt(FakeSkill())
    assert "<skill_md>" in system
    assert "Alpha does useful things." in system


def test_system_prompt_omits_empty_description(prompts):
    class NoDescription(FakeSkill):
        description = ""

    system = prompts.render_system_prompt(NoDescription())
    assert "skill 描述" not in system
    assert "Alpha does useful things." in system


def test_all_dependencies_resolve(prompts):
    for spec in prompts.by_id.values():
        for dep in spec.depends_on:
            assert dep in prompts.by_id, f"{spec.id} depends on unknown {dep}"


def test_template_syntax_error_names_the_file(tmp_path):
    """A markdown-escaped variable (`{{ x\\_y }}`, typically pasted from a chat
    window) must fail at load time with the offending file named."""
    (tmp_path / "_system.md").write_text("system prompt", encoding="utf-8")
    (tmp_path / "a.md").write_text(
        "---\noutput: IntroText\n---\nhello {{ text\\_x }}", encoding="utf-8"
    )
    with pytest.raises(ValueError, match=r"a\.md.*line 1"):
        load_prompt_set(tmp_path)


def test_topological_order_covers_every_prompt(prompts):
    order = prompts.ordered_ids()
    assert set(order) == set(prompts.by_id)
    assert len(order) == len(prompts.by_id)  # no duplicates


def test_ordering_puts_dependencies_first(tmp_path):
    """A prompt comes after every prompt it depends on."""
    _write(tmp_path, "_system.md", "system prompt")
    _write(tmp_path, "a.md", "---\noutput: IntroText\n---\nA")
    _write(tmp_path, "b.md", "---\noutput: Taglines\ndepends_on: [a]\n---\nB")
    order = load_prompt_set(tmp_path).ordered_ids()
    assert order.index("a") < order.index("b")


def test_user_prompts_are_task_only(prompts):
    """Skill context moved into _system.md: user prompts carry deps/taxonomy only."""
    spec = prompts.by_id["scenario"]
    prompt = render_user_prompt(spec, {})
    assert "Alpha" not in prompt
    assert "does useful things" not in prompt
    assert prompt.strip() == spec.template.strip()  # nothing but the task itself


def test_domain_prompt_renders_full_taxonomy(prompts):
    """Every category (emoji + name) and its description must reach the prompt."""
    prompt = render_user_prompt(prompts.by_id["domain"], {})
    for domain in Domain:
        assert f"- {domain.emoji} {domain.value}: " in prompt
    assert "agent 基础设施" not in prompt  # removed from the taxonomy
    assert "行业专业" not in prompt  # removed from the taxonomy


def test_render_uses_dependency_text(tmp_path):
    """`deps` maps a dependency's id to its parsed output object."""
    spec = _load_prompt(_write(tmp_path, "b.md", VALID_DEPENDENT))
    prompt = render_user_prompt(spec, {"scenario": IntroText(text="场景介绍内容")})
    assert "场景介绍内容" in prompt


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


VALID = """\
---
description: D
output: IntroText
---

Body {{ skill.name }}
"""

VALID_DEPENDENT = """\
---
output: Taglines
depends_on: [scenario]
---

intro: {{ deps.scenario.text }}
"""


def test_load_prompt_roundtrip(tmp_path):
    spec = _load_prompt(_write(tmp_path, "sample.md", VALID))
    assert spec.id == "sample"
    assert spec.output_model.__name__ == "IntroText"
    assert spec.depends_on == frozenset()
    assert "Body" in spec.template


def test_rejects_missing_frontmatter(tmp_path):
    path = _write(tmp_path, "bad.md", "no frontmatter here")
    with pytest.raises(ValueError, match="frontmatter"):
        _load_prompt(path)


def test_rejects_unknown_output_model(tmp_path):
    path = _write(tmp_path, "bad.md", VALID.replace("IntroText", "NoSuchModel"))
    with pytest.raises(ValueError, match="unknown output model"):
        _load_prompt(path)


def test_rejects_unknown_dependency(tmp_path):
    _write(tmp_path, "sample.md", VALID)
    orphan = VALID.replace("id: sample", "id: orphan").replace(
        "---\n\nBody", "depends_on: [nonexistent]\n---\n\nBody"
    )
    _write(tmp_path, "orphan.md", orphan)
    with pytest.raises(ValueError, match="unknown prompts"):
        load_prompt_set(tmp_path)


def test_rejects_missing_system_prompt(tmp_path):
    _write(tmp_path, "sample.md", VALID)
    with pytest.raises(FileNotFoundError):
        load_prompt_set(tmp_path)
