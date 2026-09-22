"""jev.py: the angle a chat model used to answer, now asked of the System One endpoint.

Offline like the rest of the suite: the endpoint is a stand-in client, and everything the command
does short of the call - the layout, the gate on a skill, the exit codes - runs for real.
"""

import json

import httpx
import pytest

import gen
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
    """The categories, the words for them, and the question that uses them are one object.

    They used to be two - prose in a prompt for the model and an enum in a schema for the decoder,
    with a test holding the two together. Handing the list over as `criteria` is what makes it one.
    """
    # the closed set, pinned the way the README states it: one list, and this is what it holds
    assert list(jev.CRITERIA) == [
        "development", "testing", "data-analysis", "devops-security", "office-productivity",
        "content-creation", "design-media", "knowledge-management", "business-ops",
        "finance-payment", "education", "lifestyle", "other"]
    assert all(description.strip() for description in jev.CRITERIA.values())

    question = jev.QUESTIONS["domain"]
    assert question["type"] == "choice"
    assert question["criteria"] is jev.CRITERIA
    # one rule in two numbered parts, and no rule that is a special case of it: the instruction
    # states what the taxonomy is for, the criteria state what each category holds
    assert question["instructions"].startswith("Which single category")
    assert "\n1. " in question["instructions"] and "\n2. " in question["instructions"]
    assert "education" not in question["instructions"]


def test_angles_names_what_this_script_builds(capsys):
    """The batch reads this to know which pairs are not gen.py's, so it is the only list there is."""
    assert jev.main(["--angles"]) == 0
    assert capsys.readouterr().out.split() == list(jev.QUESTIONS)


def test_an_answer_outside_the_taxonomy_is_a_failure():
    """The request used to enforce the enum. It is checked on the way in instead."""
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
    """A file holds what the endpoint answered, the way another angle's holds its schema's output:
    the label to filter on, and the distribution it was read off - the first and the second
    candidate being a difference no reader can recover from the winner alone."""
    answer = {"domain": {"type": "choice", "choice": "design-media", "confidence": 0.47,
                         "probabilities": {"design-media": 0.52, "development": 0.48}}}
    assert jev.profile(answer) == {"domain": "design-media", "confidence": 0.47,
                                   "probabilities": {"design-media": 0.52, "development": 0.48}}
    assert jev.probabilities("testing") == {}  # nothing to read one from
    assert jev.probabilities({"choice": "testing"}) == {}


# ------------------------------------------------------------------ the request


def test_print_sends_the_state_and_the_questions_and_no_messages(workdir, capsys):
    """The one thing that separates this from gen.py's path: no chat, no schema, no text.

    Printed from `workdir`, where there is no `.env`: a request that needs no key is the point of
    `just render`.
    """
    assert jev.main(["--print", "domain", ALPHA]) == 0
    body = json.loads(capsys.readouterr().out)

    assert body["model"] == "jev-latest"
    assert body["state"].startswith("你是一位拥有某项技能")
    assert ALPHA in body["state"]  # the name the system message leads with
    assert body["questions"]["domain"]["type"] == "choice"
    assert set(body["questions"]["domain"]["criteria"]) == set(jev.CRITERIA)
    assert "messages" not in body


def test_ask_posts_the_state_and_the_questions():
    seen: dict = {}

    class Fake:
        def post(self, url, headers=None, json=None):
            seen.update({"url": url, "headers": headers, "json": json})
            return httpx.Response(200, json={"answers": {"domain": {"choice": "testing"}}},
                                  request=httpx.Request("POST", url))

    client = jev.Jev(jev.JevConfig(api_key="k"), client=Fake())
    answers = client.ask(jev.request("jev-latest", "STATE", {"domain": {"type": "choice"}}))

    assert answers == {"domain": {"choice": "testing"}}
    assert seen["url"] == jev.BASE_URL
    assert seen["headers"] == {"Authorization": "Bearer k"}
    assert set(seen["json"]) == {"model", "state", "questions"}


def test_a_dropped_call_is_retried(monkeypatch):
    """The endpoint regularly drops the first call after it has been idle, which arrives as a
    timeout: retrying keeps that from being recorded as a skill that cannot be built."""
    calls = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            if len(calls) == 1:
                raise httpx.ReadTimeout("no response")
            return httpx.Response(200, json={"answers": {"domain": {"choice": "testing"}}},
                                  request=httpx.Request("POST", url))

    monkeypatch.setattr(jev.time, "sleep", lambda seconds: None)
    client = jev.Jev(jev.JevConfig(api_key="k", max_retries=2), client=Fake())

    assert client.ask({}) == {"domain": {"choice": "testing"}}
    assert len(calls) == 2


def test_a_rejected_body_is_not_retried():
    calls = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            return httpx.Response(400, text="bad request", request=httpx.Request("POST", url))

    client = jev.Jev(jev.JevConfig(api_key="k", max_retries=3), client=Fake())
    with pytest.raises(httpx.HTTPStatusError):
        client.ask({})
    assert len(calls) == 1


def test_worth_retrying():
    """A dropped connection or a busy gateway is worth the next try; a rejected body is not."""
    request = httpx.Request("POST", jev.BASE_URL)
    assert jev.worth_retrying(httpx.ReadTimeout("dropped"))
    for code in (429, 500, 502, 503, 504):
        error = httpx.HTTPStatusError("busy", request=request,
                                      response=httpx.Response(code, request=request))
        assert jev.worth_retrying(error)
    error = httpx.HTTPStatusError("no", request=request,
                                  response=httpx.Response(400, request=request))
    assert not jev.worth_retrying(error)


def test_no_key_is_no_call(workdir, monkeypatch):
    """A key in the developer's environment cannot answer for one that is not in `.env`."""
    monkeypatch.delenv("SKILLS_PROFILES_JEV_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="SKILLS_PROFILES_JEV_API_KEY"):
        jev.Jev(jev.JevConfig())


# ------------------------------------------------------------------ the repository


def test_the_repository_reaches_the_state(workdir):
    """The one layer a chat angle is not handed: the siblings' own lines, beside the skill's parts."""
    config = gen.Config()
    path = gen.skill_source_path(config, ALPHA).parent.parent / "beta"
    path.mkdir()
    (path / gen.SKILL_MD).write_text(
        "---\nname: beta\ndescription: Drafts a release note.\n---\n\nbody\n", encoding="utf-8")

    state = jev.state(config, ALPHA, gen.skill_source(config, ALPHA))

    assert "<repository>" in state
    assert "<id>owner-a/repo-a</id>" in state
    assert "- beta: Drafts a release note." in state


def test_a_lone_skill_gets_no_repository(workdir, capsys):
    """A repository with no sibling is not invented into the state, and `--print` shows the same."""
    config = gen.Config()
    assert "<repository>" not in jev.state(config, ALPHA, gen.skill_source(config, ALPHA))

    assert jev.main(["--print", "domain", ALPHA]) == 0
    assert "<repository>" not in json.loads(capsys.readouterr().out)["state"]


# ------------------------------------------------------------------ the command


def test_a_dry_run_writes_the_layout_without_calling(config):
    """`just dry=1` is offline, and the tree it leaves is the tree a real run leaves."""
    assert jev.main(["domain", ALPHA]) == 0

    written = json.loads(gen.json_path(config, "domain", ALPHA).read_text(encoding="utf-8"))
    assert written["domain"] == "development"
    assert written["confidence"] == 1.0
    assert set(written["probabilities"]) == set(jev.CRITERIA)  # every option, as a real answer has
    assert sum(written["probabilities"].values()) == 1.0
    assert gen.markdown_path(config, "domain", ALPHA).is_file()


def test_main_writes_one_output(workdir, monkeypatch):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    monkeypatch.setattr(jev, "Jev", FakeJev)
    config = gen.Config()

    assert jev.main(["domain", ALPHA]) == 0

    assert json.loads(gen.json_path(config, "domain", ALPHA).read_text(encoding="utf-8")) == {
        "domain": "testing", "confidence": 0.9, "probabilities": {"testing": 0.9, "other": 0.1}}
    markdown = gen.markdown_path(config, "domain", ALPHA).read_text(encoding="utf-8")
    assert markdown.startswith(f"# alpha (`{ALPHA}`)\n\n## domain\n")
    assert "### domain\n\ntesting" in markdown
    assert "### confidence\n\n0.9" in markdown
    assert "### probabilities\n\ntesting: 0.9, other: 0.1" in markdown  # as a reader sees the answer


def test_a_skill_no_description_can_be_read_from_is_dropped(workdir, capsys):
    """The same gate gen.py applies: nothing to lead the state with is nothing to build."""
    config = gen.Config()
    gen.skill_source_path(config, ALPHA).write_text("Just a body.\n", encoding="utf-8")

    assert jev.main(["domain", ALPHA]) == 1
    assert not gen.json_path(config, "domain", ALPHA).exists()
    assert "no description in its front matter" in capsys.readouterr().err


def test_a_call_that_fails_is_one_line_and_status_one(workdir, monkeypatch, capsys):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")

    class Broken:
        def __init__(self, config, client=None):
            pass

        def ask(self, body: dict) -> dict:
            raise httpx.ReadTimeout("dropped")

    monkeypatch.setattr(jev, "Jev", Broken)

    assert jev.main(["domain", ALPHA]) == 1
    assert not gen.json_path(gen.Config(), "domain", ALPHA).exists()
    assert "ReadTimeout" in capsys.readouterr().err


def test_bad_arguments_are_status_two(capsys):
    assert jev.main([]) == 2
    assert jev.main(["nosuchangle", ALPHA]) == 2
    assert "usage: jev.py" in capsys.readouterr().err
