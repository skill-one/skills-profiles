"""jev.py: the one skill in, one typed question out, one domain.json written.

Offline like the rest of the suite: the endpoint is a stand-in client, and everything the command
does short of the call - the source reading, the state, the layout, the gate on a skill, the exit
codes - runs for real.
"""

import json

import httpx
import pytest

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


# ------------------------------------------------------------- the skill source


def test_a_short_source_is_passed_through_untouched(config):
    """No note, no reflow: the cap is the only thing that ever changes a source, and dropping the
    front matter is `skill_body`'s job rather than this one's."""
    source = jev.skill_source(config, ALPHA)
    assert source.startswith("---\nname: owner-a/repo-a/alpha\ndescription: Tidies a note list")
    assert source.endswith("---\n\nowner-a/repo-a/alpha does useful things.\n")


def test_the_sent_body_leaves_the_front_matter_behind(config):
    """The name and the description lead the state, so the copy of them at the top of the file is
    not sent a second time: the body starts at the first line that says something new."""
    body = jev.skill_body(jev.skill_source(config, ALPHA))

    assert body == "owner-a/repo-a/alpha does useful things.\n"


def test_a_source_with_no_front_matter_is_sent_as_it_is(workdir):
    """A file with nothing to drop is not a file to guess about: the strip is anchored at the top,
    and what upstream wrote is what the endpoint reads."""
    text = "Just a body.\n\n---\n\nStill the body.\n"
    jev.skill_source_path(jev.Config(), ALPHA).write_text(text, encoding="utf-8")

    assert jev.skill_body(jev.skill_source(jev.Config(), ALPHA)) == text


def test_the_description_comes_from_the_skills_own_front_matter(config):
    """The index upstream publishes no longer carries one, so the file is the source."""
    assert jev.skill_description(jev.skill_source(config, ALPHA)).startswith("Tidies a note list")


def test_a_description_is_read_as_yaml_not_off_the_line(workdir):
    """A `description:` is a YAML value: `>` folds its lines and quotes unescape theirs."""
    config = jev.Config()
    path = jev.skill_source_path(config, ALPHA)

    path.write_text("---\nname: alpha\ndescription: >-\n  Folds two lines\n  into one.\n---\n\nbody\n",
                    encoding="utf-8")
    assert jev.skill_description(jev.skill_source(config, ALPHA)) == "Folds two lines into one."

    path.write_text('---\nname: alpha\ndescription: "Says \\"hi\\" and stops."\n---\n\nbody\n',
                    encoding="utf-8")
    assert jev.skill_description(jev.skill_source(config, ALPHA)) == 'Says "hi" and stops.'


def test_a_skill_whose_front_matter_yields_no_description_is_dropped(workdir, capsys):
    """Nothing to lead the state with is nothing to label, so the skill is dropped - no call, no
    file. The three ways to have nothing: no header, no `description:`, header that is not YAML."""
    config = jev.Config()
    path = jev.skill_source_path(config, ALPHA)

    for text in ["Just a body, no header.\n",
                 "---\nname: alpha\n---\n\nA header with no description.\n",
                 "---\nname: alpha\ndescription: DEPRECATED: renamed elsewhere\n---\n\nBody.\n"]:
        path.write_text(text, encoding="utf-8")
        assert jev.skill_description(jev.skill_source(config, ALPHA)) == ""
        assert jev.main([ALPHA]) == 1
        assert not jev.json_path(config, ALPHA).exists()
        assert "no description in its front matter" in capsys.readouterr().err


def test_a_long_source_is_cut_on_a_line_break_and_says_so(workdir):
    """Mid-line would hand over a heading or a table in half; silent would read as a source that
    simply ended. Both halves are checked."""
    config = jev.Config()
    body = "".join(f"line {i:04d} " + "x" * 40 + "\n" for i in range(500))
    assert len(body) > jev.MAX_SKILL_MD_CHARS
    jev.skill_source_path(config, ALPHA).write_text(body, encoding="utf-8")

    source = jev.skill_source(config, ALPHA)

    head = source.removesuffix(f"\n\n{jev.TRUNCATION_NOTE}\n")
    assert head != source  # the note is there, at the end
    assert len(source) < len(body)  # and something really was dropped
    assert len(head) <= jev.MAX_SKILL_MD_CHARS  # never past the budget
    assert body.startswith(head + "\n")  # a prefix of the file, ending at a line end
    assert all(line.startswith("line ") for line in head.splitlines())  # whole lines only


# ------------------------------------------------------------------ the repository


def add_sibling(config: jev.Config, slug: str, description: str) -> None:
    """One more skill beside ALPHA's, the way the mirror nests a repository: `owner/repo/slug`."""
    path = jev.skill_source_path(config, ALPHA).parent.parent / slug
    path.mkdir()
    (path / jev.SKILL_MD).write_text(
        f"---\nname: {slug}\ndescription: {description}\n---\n\nbody\n", encoding="utf-8")


def test_the_repository_is_the_directory_above_the_skill_not_the_skills_own(workdir):
    """The tree nests `owner/repo/slug`, so a file inside the skill's own directory is not a
    sibling: the one that matters sits one level up."""
    config = jev.Config()
    own = jev.skill_source_path(config, ALPHA).parent
    (own / "nested").mkdir()
    (own / "nested" / jev.SKILL_MD).write_text("---\nname: x\ndescription: y\n---\n", encoding="utf-8")
    assert jev.repository(config, ALPHA) is None

    add_sibling(config, "beta", "Drafts a release note.")
    assert jev.repository(config, ALPHA)["siblings"] == ["beta: Drafts a release note."]


def test_the_repository_is_the_siblings_beside_the_skill_and_never_itself(workdir):
    """The directory above the skill is the repository; a sibling gives its one line, not its body."""
    config = jev.Config()
    add_sibling(config, "beta", "Drafts a release note.")
    add_sibling(config, "gamma", "Trims the note down.")

    assert jev.repository(config, ALPHA) == {
        "id": "owner-a/repo-a",
        "siblings": ["beta: Drafts a release note.", "gamma: Trims the note down."],
        "more": 0}


def test_a_repository_with_no_sibling_is_not_sent(workdir):
    """Nothing the skill's own name has not said, so no empty block is invented."""
    assert jev.repository(jev.Config(), ALPHA) is None


def test_a_sibling_with_no_description_is_named_without_one(workdir):
    """The slug is still a signal; a header nothing can be read from is not a reason to drop it."""
    config = jev.Config()
    path = jev.skill_source_path(config, ALPHA).parent.parent / "beta"
    path.mkdir()
    (path / jev.SKILL_MD).write_text("Just a body.\n", encoding="utf-8")

    assert jev.repository(config, ALPHA)["siblings"] == ["beta"]


def test_only_the_first_siblings_are_sent_and_the_rest_are_counted(workdir, monkeypatch):
    """A `awesome-*` collection cannot blow the request up: the cap holds and the rest are
    counted."""
    monkeypatch.setattr(jev, "MAX_SIBLINGS", 1)
    config = jev.Config()
    add_sibling(config, "beta", "First.")
    add_sibling(config, "gamma", "Second.")

    assert jev.repository(config, ALPHA) == {
        "id": "owner-a/repo-a", "siblings": ["beta: First."], "more": 1}


def test_a_sibling_description_is_cut_to_a_hint(workdir):
    """A sibling's own description is sometimes a page: cut at a word so a repo of them cannot
    dwarf the skill's own body."""
    config = jev.Config()
    add_sibling(config, "beta", "word " * 200)

    line = jev.repository(config, ALPHA)["siblings"][0]

    assert line.startswith("beta: word word")
    assert line.endswith("…") and "  " not in line
    assert len(line) <= len("beta: ") + jev.MAX_SIBLING_CHARS + 1


# ------------------------------------------------------------------ the request


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


def test_ask_posts_the_state_and_the_questions():
    seen: dict = {}

    class Fake:
        def post(self, url, headers=None, json=None):
            seen.update({"url": url, "headers": headers, "json": json})
            return httpx.Response(200, json={"answers": {"domain": {"choice": "testing"}}},
                                  request=httpx.Request("POST", url))

    client = jev.Jev(jev.Config(api_key="k", base_url=jev.BASE_URL), client=Fake())
    answers = client.ask(jev.request_body("jev-latest", "STATE"))

    assert answers == {"domain": {"choice": "testing"}}
    assert seen["url"] == jev.BASE_URL
    assert seen["headers"] == {"Authorization": "Bearer k"}
    assert set(seen["json"]) == {"model", "state", "questions"}


def test_a_dropped_call_is_retried(monkeypatch):
    """The endpoint regularly drops the first call after it has been idle, which arrives as a
    timeout: retrying keeps that from being recorded as a skill that cannot be labelled."""
    calls = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            if len(calls) == 1:
                raise httpx.ReadTimeout("no response")
            return httpx.Response(200, json={"answers": {"domain": {"choice": "testing"}}},
                                  request=httpx.Request("POST", url))

    monkeypatch.setattr(jev.time, "sleep", lambda seconds: None)
    client = jev.Jev(jev.Config(api_key="k", max_retries=2), client=Fake())

    assert client.ask({}) == {"domain": {"choice": "testing"}}
    assert len(calls) == 2


def test_a_rejected_body_is_not_retried():
    calls = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            return httpx.Response(400, text="bad request", request=httpx.Request("POST", url))

    client = jev.Jev(jev.Config(api_key="k", max_retries=3), client=Fake())
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
    monkeypatch.delenv("SKILLS_PROFILES_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="SKILLS_PROFILES_API_KEY"):
        jev.Jev(jev.Config())


def test_the_repository_reaches_the_state(workdir):
    """The one extra layer: the siblings' own lines, beside the skill's own parts."""
    config = jev.Config()
    path = jev.skill_source_path(config, ALPHA).parent.parent / "beta"
    path.mkdir()
    (path / jev.SKILL_MD).write_text(
        "---\nname: beta\ndescription: Drafts a release note.\n---\n\nbody\n", encoding="utf-8")

    rendered = jev.state(config, ALPHA, jev.skill_source(config, ALPHA))

    assert "<repository>" in rendered
    assert "<id>owner-a/repo-a</id>" in rendered
    assert "- beta: Drafts a release note." in rendered


def test_a_lone_skill_gets_no_repository(workdir, capsys):
    """A repository with no sibling is not invented into the state, and `--print` shows the same."""
    config = jev.Config()
    assert "<repository>" not in jev.state(config, ALPHA, jev.skill_source(config, ALPHA))

    assert jev.main(["--print", ALPHA]) == 0
    assert "<repository>" not in json.loads(capsys.readouterr().out)["state"]


# ------------------------------------------------------------------ the output


def test_write_writes_one_json(config):
    path = jev.write(config, ALPHA, {"domain": "testing", "confidence": 1.0, "probabilities": {}})
    assert path == jev.json_path(config, ALPHA)
    assert json.loads(path.read_text(encoding="utf-8"))["domain"] == "testing"
    assert not path.with_name(path.name + ".part").exists()  # renamed into place


# ---------------------------------------------------------------------- main


def test_a_dry_run_writes_the_layout_without_calling(config):
    """`just dry=1` is offline, and the tree it leaves is the tree a real run leaves."""
    assert jev.main([ALPHA]) == 0

    written = json.loads(jev.json_path(config, ALPHA).read_text(encoding="utf-8"))
    assert written["domain"] == "development"
    assert written["confidence"] == 1.0
    assert set(written["probabilities"]) == set(jev.CRITERIA)  # every option, as a real answer has
    assert sum(written["probabilities"].values()) == 1.0


def test_main_writes_one_output(workdir, monkeypatch):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    monkeypatch.setattr(jev, "Jev", FakeJev)
    config = jev.Config()

    assert jev.main([ALPHA]) == 0

    assert json.loads(jev.json_path(config, ALPHA).read_text(encoding="utf-8")) == {
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
    assert not jev.json_path(jev.Config(), ALPHA).exists()
    assert "ReadTimeout" in capsys.readouterr().err


def test_a_missing_skill_is_a_message_not_a_traceback(workdir, capsys):
    """A skill that is not there is the caller's typo to fix: exit 1 with the path, never a
    traceback."""
    assert jev.main(["owner-a/repo-a/nope"]) == 1
    assert "not found" in capsys.readouterr().err


def test_bad_arguments_are_status_two(capsys):
    assert jev.main([]) == 2
    assert "usage: jev.py" in capsys.readouterr().err
