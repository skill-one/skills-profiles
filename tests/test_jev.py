"""jev.py: the one skill in, one typed question out, one domain.json written.

Offline like the rest of the suite: the endpoint is a stand-in client, and everything the command
does short of the call - the state, the taxonomy, the layout, the gate on a skill, the exit codes -
runs for real. The source reading, the writes and the retries it shares live in test_common.py.
"""

import json

import httpx
import pytest

import common
import jev

ALPHA = "owner-a/repo-a/alpha"


class FakeJev:
    """A stand-in endpoint: one choice, or whatever the test wants to see go wrong."""

    def __init__(self, config, client=None):
        self.answers = {"domain": {"type": "choice", "choice": "testing", "confidence": 0.9,
                                   "probabilities": {"testing": 0.9, "other": 0.1}}}

    def ask(self, body: dict) -> dict:
        return self.answers


# ------------------------------------------------------------------ the taxonomy


def test_the_taxonomy_is_stated_once():
    """The categories, the words for them, and the question that uses them are one object."""
    # the closed set, pinned the way the README states it: one list, and this is what it holds
    assert list(jev.CRITERIA) == [
        "development", "testing", "data-analysis", "devops-security", "office-productivity",
        "content-creation", "design-media", "knowledge-management", "business-ops",
        "finance-payment", "education", "lifestyle", "other"]
    assert all(description.strip() for description in jev.CRITERIA.values())

    question = jev.QUESTION["domain"]
    assert question["type"] == "choice"
    assert question["criteria"] is jev.CRITERIA
    # one rule in two numbered parts, and no rule that is a special case of it
    assert question["instructions"].startswith("Which single category")
    assert "\n1. " in question["instructions"] and "\n2. " in question["instructions"]
    assert "education" not in question["instructions"]
    assert set(jev.request_body("jev-latest", "STATE")["questions"]) == {"domain"}


def test_an_answer_outside_the_taxonomy_is_a_failure():
    """The request no longer enforces the enum. It is checked on the way in instead."""
    with pytest.raises(RuntimeError, match="not a category"):
        jev.profile({"domain": {"choice": "marketing"}})
    with pytest.raises(RuntimeError, match="not a category"):
        jev.profile({})


def test_the_answer_readers_take_the_option_and_the_confidence():
    assert jev.choice({"choice": "testing", "confidence": 0.9}) == "testing"
    assert jev.choice("testing") == "testing"
    assert jev.choice(None) is None
    assert jev.choice({"confidence": 0.9}) is None
    assert jev.confidence({"choice": "testing", "confidence": 0.9}) == 0.9
    assert jev.confidence({"choice": "testing"}) is None
    assert jev.confidence("testing") is None


def test_the_profile_keeps_the_whole_answer():
    """The label to filter on, and the distribution it was read off - the second candidate being a
    difference no reader can recover from the winner alone."""
    answer = {"domain": {"type": "choice", "choice": "design-media", "confidence": 0.47,
                         "probabilities": {"design-media": 0.52, "development": 0.48}}}
    assert jev.profile(answer) == {"domain": "design-media", "confidence": 0.47,
                                   "probabilities": {"design-media": 0.52, "development": 0.48}}
    assert jev.probabilities("testing") == {}  # nothing to read one from
    assert jev.probabilities({"choice": "testing"}) == {}


# ------------------------------------------------------------------ the state


def test_print_sends_the_state_and_the_questions_and_no_messages(workdir, capsys):
    """The one thing this endpoint takes: no chat, no schema, no text. Printed from `workdir`,
    where there is no `.env`: a request that needs no key is the point of `just render`."""
    assert jev.main(["--print", ALPHA]) == 0
    body = json.loads(capsys.readouterr().out)

    assert body["model"] == "jev-latest"
    assert body["state"].startswith("你是一位拥有某项技能")
    assert ALPHA in body["state"]  # the name the state leads with
    assert body["questions"]["domain"]["type"] == "choice"
    assert set(body["questions"]["domain"]["criteria"]) == set(jev.CRITERIA)
    assert "messages" not in body


def test_the_repository_reaches_the_state(workdir):
    """The one extra layer: the siblings' own lines, beside the skill's own parts."""
    config = common.Config()
    path = common.skill_md_path(config, ALPHA).parent.parent / "beta"
    path.mkdir()
    (path / common.SKILL_MD).write_text(
        "---\nname: beta\ndescription: Drafts a release note.\n---\n\nbody\n", encoding="utf-8")

    rendered = jev.state(config, ALPHA, common.skill_source(config, ALPHA))

    assert "<repository>" in rendered
    assert "<id>owner-a/repo-a</id>" in rendered
    assert "- beta: Drafts a release note." in rendered


def test_a_lone_skill_gets_no_repository(workdir, capsys):
    """A repository with no sibling is not invented into the state, and `--print` shows the same."""
    config = common.Config()
    assert "<repository>" not in jev.state(config, ALPHA, common.skill_source(config, ALPHA))

    assert jev.main(["--print", ALPHA]) == 0
    assert "<repository>" not in json.loads(capsys.readouterr().out)["state"]


# -------------------------------------------------------------------- the call


def test_ask_posts_the_state_and_the_questions():
    seen: dict = {}

    class Fake:
        def post(self, url, headers=None, json=None):
            seen.update({"url": url, "headers": headers, "json": json})
            return httpx.Response(200, json={"answers": {"domain": {"choice": "testing"}}},
                                  request=httpx.Request("POST", url))

    client = jev.Jev(common.Config(api_key="k", base_url=common.DOMAIN_BASE_URL), client=Fake())
    answers = client.ask(jev.request_body("jev-latest", "STATE"))

    assert answers == {"domain": {"choice": "testing"}}
    assert seen["url"] == common.DOMAIN_BASE_URL
    assert seen["headers"] == {"Authorization": "Bearer k"}
    assert set(seen["json"]) == {"model", "state", "questions"}


def test_no_key_is_no_call(workdir, monkeypatch):
    """A key in the developer's environment cannot answer for one that is not in `.env`."""
    monkeypatch.delenv("SKILLS_PROFILES_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="SKILLS_PROFILES_API_KEY"):
        jev.Jev(common.Config())


# ---------------------------------------------------------------------- main


def test_a_skill_whose_front_matter_yields_no_description_is_dropped(workdir, capsys):
    """Nothing to lead the state with is nothing to label, so the skill is dropped - no call, no
    file. The three ways to have nothing: no header, no `description:`, header that is not YAML."""
    config = common.Config()
    path = common.skill_md_path(config, ALPHA)

    for text in ["Just a body, no header.\n",
                 "---\nname: alpha\n---\n\nA header with no description.\n",
                 "---\nname: alpha\ndescription: DEPRECATED: renamed elsewhere\n---\n\nBody.\n"]:
        path.write_text(text, encoding="utf-8")
        assert common.skill_description(common.skill_source(config, ALPHA)) == ""
        assert jev.main([ALPHA]) == 1
        assert not common.profile_path(config, ALPHA, common.DOMAIN_ANGLE).exists()
        assert "no description in its front matter" in capsys.readouterr().err


def test_a_dry_run_writes_the_layout_without_calling(config):
    """`just dry=1` is offline, and the tree it leaves is the tree a real run leaves."""
    assert jev.main([ALPHA]) == 0

    written = json.loads(
        common.profile_path(config, ALPHA, common.DOMAIN_ANGLE).read_text(encoding="utf-8"))
    assert written["domain"] == "development"
    assert written["confidence"] == 1.0
    assert set(written["probabilities"]) == set(jev.CRITERIA)  # every option, as a real answer has
    assert sum(written["probabilities"].values()) == 1.0


def test_main_writes_one_output(workdir, monkeypatch):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    monkeypatch.setattr(jev, "Jev", FakeJev)
    config = common.Config()

    assert jev.main([ALPHA]) == 0

    assert json.loads(common.profile_path(
        config, ALPHA, common.DOMAIN_ANGLE).read_text(encoding="utf-8")) == {
        "domain": "testing", "confidence": 0.9, "probabilities": {"testing": 0.9, "other": 0.1}}


def test_a_call_that_fails_is_one_line_and_status_one(workdir, monkeypatch, capsys):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")

    class Broken:
        def __init__(self, config, client=None):
            pass

        def ask(self, body: dict) -> dict:
            raise httpx.ReadTimeout("dropped")

    monkeypatch.setattr(jev, "Jev", Broken)

    assert jev.main([ALPHA]) == 1
    assert not common.profile_path(common.Config(), ALPHA, common.DOMAIN_ANGLE).exists()
    assert "ReadTimeout" in capsys.readouterr().err


def test_a_missing_skill_is_a_message_not_a_traceback(workdir, capsys):
    """A skill that is not there is the caller's typo to fix: exit 1 with the path, never a
    traceback."""
    assert jev.main(["owner-a/repo-a/nope"]) == 1
    assert "not found" in capsys.readouterr().err


def test_bad_arguments_are_status_two(capsys):
    assert jev.main([]) == 2
    assert "usage: jev.py" in capsys.readouterr().err
