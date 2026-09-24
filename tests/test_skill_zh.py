"""skill_zh.py: the third angle - one skill's SKILL.md body in, one Chinese page out.

Offline like test_translate: the chat endpoint is a stand-in, and everything the command does
short of the call - the body reading, the request messages, the layout, the gates, the exit
codes - runs for real.
"""

import json

import pytest

import common
import skill_zh
import translate

ALPHA = "owner-a/repo-a/alpha"
ZH = "# 整理笔记\n\n把零散的头绪折进一份持续更新的索引，并让整堆内容可搜索。\n"


class FakeTranslator:
    """A stand-in endpoint: one fixed Chinese page body."""

    def __init__(self, config, client=None):
        pass

    def ask(self, body: dict) -> str:
        return ZH


def source(config) -> str:
    return common.skill_md_path(config, ALPHA).read_text(encoding="utf-8")


# ------------------------------------------------------------------ the request


def test_the_request_is_one_chat_turn(config):
    """The same OpenAI shape as the description angle, with the skill's body as the one user turn
    rendered from the prompt files."""
    body = skill_zh._request(config, ALPHA, source(config), "desc")
    system = common.render(common.load_prompt(config, skill_zh.PROMPT), to=skill_zh.TO)
    user = common.render(common.load_prompt(config, skill_zh.USER_PROMPT),
                         to=skill_zh.TO, text=common.skill_body(source(config)))

    assert body["model"] == common.TRANSLATE_MODEL
    assert body["messages"] == [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    assert "简体中文" in system  # {{to}} rendered, in both turns
    assert "{{" not in system and "{{" not in user
    assert "markdown" in system  # preserving the formatting is the task's own requirement


def test_the_front_matter_is_not_sent(workdir, capsys):
    """Only the body crosses the endpoint: the front matter is metadata, and the description has
    its own angle."""
    assert skill_zh.main(["--print", ALPHA]) == 0
    body = json.loads(capsys.readouterr().out)

    user = body["messages"][1]["content"]
    assert user.startswith(f"Translate to {skill_zh.TO}:")
    assert "does useful things" in user  # the body, carried by the user template
    assert "Tidies a note list" not in user  # the description lives in the front matter


def test_braces_in_a_body_are_data_not_template(workdir):
    """The body is a Jinja *value*, not part of the template: braces a skill writes are sent as
    written and can never trip the renderer."""
    config = common.Config()
    common.skill_md_path(config, ALPHA).write_text(
        "---\nname: alpha\ndescription: d\n---\n\nUse {{placeholder}} as written.\n",
        encoding="utf-8")

    body = skill_zh._request(config, ALPHA, source(config), "d")

    assert "{{placeholder}}" in body["messages"][1]["content"]


# -------------------------------------------------------------------- the output


def test_a_dry_run_writes_the_layout_without_calling(config):
    """`just dry=1 skill-zh` is offline, and the tree it leaves is the tree a real run leaves."""
    assert skill_zh.main([ALPHA]) == 0

    path = common.profile_path(config, ALPHA, common.SKILL_ZH_ANGLE).with_suffix(".md")
    assert path == common.profile_dir(config, ALPHA) / "skill_zh.md"
    assert path.read_text(encoding="utf-8").startswith("【占位】")  # identifiable as a placeholder


def test_main_writes_the_translation_alone(workdir, monkeypatch):
    """The page is the translation and nothing else - the identifying metadata lives in the
    catalog, and the reasoning or whitespace of the endpoint never reaches the disk."""
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    monkeypatch.setattr(translate, "Translator", FakeTranslator)

    assert skill_zh.main([ALPHA]) == 0

    config = common.Config()
    text = (common.profile_path(config, ALPHA, common.SKILL_ZH_ANGLE)
            .with_suffix(".md")).read_text(encoding="utf-8")
    assert text == f"{ZH.strip()}\n"
    assert "description:" not in text  # no front matter rides along


def test_a_too_long_body_is_dropped_whole(workdir, monkeypatch):
    """A half-translated page must never pass for a whole one: past the cap nothing is written
    and the skill is unusable input, like one without a description."""
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")  # the gate is a real request's gate
    config = common.Config()
    common.skill_md_path(config, ALPHA).write_text(
        "---\nname: alpha\ndescription: d\n---\n\n" + "a" * (skill_zh.MAX_BODY_CHARS + 1),
        encoding="utf-8")

    with pytest.raises(SystemExit, match="not translated"):
        skill_zh.main([ALPHA])

    assert not common.profile_path(
        config, ALPHA, common.SKILL_ZH_ANGLE).with_suffix(".md").exists()


def test_an_empty_body_is_dropped_whole(workdir, monkeypatch):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    config = common.Config()
    common.skill_md_path(config, ALPHA).write_text(
        "---\nname: alpha\ndescription: d\n---\n\n   \n", encoding="utf-8")

    with pytest.raises(SystemExit, match="not translated"):
        skill_zh.main([ALPHA])

    assert not common.profile_path(
        config, ALPHA, common.SKILL_ZH_ANGLE).with_suffix(".md").exists()


def test_a_call_that_fails_is_one_line_and_status_one(workdir, monkeypatch, capsys):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")

    class Broken:
        def __init__(self, config, client=None):
            pass

        def ask(self, body: dict) -> str:
            raise RuntimeError("response carries no translation")

    monkeypatch.setattr(translate, "Translator", Broken)

    assert skill_zh.main([ALPHA]) == 1
    assert not common.profile_path(
        common.Config(), ALPHA, common.SKILL_ZH_ANGLE).with_suffix(".md").exists()
    assert "RuntimeError" in capsys.readouterr().err


def test_a_missing_skill_is_a_message_not_a_traceback(workdir, capsys):
    assert skill_zh.main(["owner-a/repo-a/nope"]) == 1
    assert "not found" in capsys.readouterr().err


def test_bad_arguments_are_status_two(capsys):
    assert skill_zh.main([]) == 2
    assert "usage: skill_zh.py" in capsys.readouterr().err
