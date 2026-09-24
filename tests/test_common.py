"""common.py: the kernel both producers share.

The skill source both angles are built from, the repository disambiguation, the prompt files, the
atomic writes, and the one retry reading the two endpoints use. The commands themselves are
exercised through test_jev.py and test_translate.py.
"""

import httpx
import pytest

import common
import translate

ALPHA = "owner-a/repo-a/alpha"


# ------------------------------------------------------------- the skill source


def test_a_short_source_is_passed_through_untouched(config):
    """No note, no reflow: the cap is the only thing that ever changes a source, and dropping the
    front matter is `skill_body`'s job rather than this one's."""
    source = common.skill_source(config, ALPHA)
    assert source.startswith("---\nname: owner-a/repo-a/alpha\ndescription: Tidies a note list")
    assert source.endswith("---\n\nowner-a/repo-a/alpha does useful things.\n")


def test_the_sent_body_leaves_the_front_matter_behind(config):
    """The name and the description lead the state, so the copy of them at the top of the file is
    not sent a second time: the body starts at the first line that says something new."""
    body = common.skill_body(common.skill_source(config, ALPHA))

    assert body == "owner-a/repo-a/alpha does useful things.\n"


def test_a_source_with_no_front_matter_is_sent_as_it_is(workdir):
    """A file with nothing to drop is not a file to guess about: the strip is anchored at the top,
    and what upstream wrote is what the endpoint reads."""
    text = "Just a body.\n\n---\n\nStill the body.\n"
    common.skill_md_path(common.Config(), ALPHA).write_text(text, encoding="utf-8")

    assert common.skill_body(common.skill_source(common.Config(), ALPHA)) == text


def test_the_description_comes_from_the_skills_own_front_matter(config):
    """The index upstream publishes no longer carries one, so the file is the source."""
    assert common.skill_description(common.skill_source(config, ALPHA)).startswith(
        "Tidies a note list")


def test_a_description_is_read_as_yaml_not_off_the_line(workdir):
    """A `description:` is a YAML value: `>` folds its lines and quotes unescape theirs."""
    config = common.Config()
    path = common.skill_md_path(config, ALPHA)

    path.write_text("---\nname: alpha\ndescription: >-\n  Folds two lines\n  into one.\n---\n\nbody\n",
                    encoding="utf-8")
    assert common.skill_description(common.skill_source(config, ALPHA)) == "Folds two lines into one."

    path.write_text('---\nname: alpha\ndescription: "Says \\"hi\\" and stops."\n---\n\nbody\n',
                    encoding="utf-8")
    assert common.skill_description(common.skill_source(config, ALPHA)) == 'Says "hi" and stops.'


def test_a_long_source_is_cut_on_a_line_break_and_says_so(workdir):
    """Mid-line would hand over a heading or a table in half; silent would read as a source that
    simply ended. Both halves are checked."""
    config = common.Config()
    body = "".join(f"line {i:04d} " + "x" * 40 + "\n" for i in range(500))
    assert len(body) > common.MAX_SKILL_MD_CHARS
    common.skill_md_path(config, ALPHA).write_text(body, encoding="utf-8")

    source = common.skill_source(config, ALPHA)

    head = source.removesuffix(f"\n\n{common.TRUNCATION_NOTE}\n")
    assert head != source  # the note is there, at the end
    assert len(source) < len(body)  # and something really was dropped
    assert len(head) <= common.MAX_SKILL_MD_CHARS  # never past the budget
    assert body.startswith(head + "\n")  # a prefix of the file, ending at a line end
    assert all(line.startswith("line ") for line in head.splitlines())  # whole lines only


# ------------------------------------------------------------------ the repository


def add_sibling(config: common.Config, slug: str, description: str) -> None:
    """One more skill beside ALPHA's, the way the mirror nests a repository: `owner/repo/slug`."""
    path = common.skill_md_path(config, ALPHA).parent.parent / slug
    path.mkdir()
    (path / common.SKILL_MD).write_text(
        f"---\nname: {slug}\ndescription: {description}\n---\n\nbody\n", encoding="utf-8")


def test_the_repository_is_the_directory_above_the_skill_not_the_skills_own(workdir):
    """The tree nests `owner/repo/slug`, so a file inside the skill's own directory is not a
    sibling: the one that matters sits one level up."""
    config = common.Config()
    own = common.skill_md_path(config, ALPHA).parent
    (own / "nested").mkdir()
    (own / "nested" / common.SKILL_MD).write_text(
        "---\nname: x\ndescription: y\n---\n", encoding="utf-8")
    assert common.repository(config, ALPHA) is None

    add_sibling(config, "beta", "Drafts a release note.")
    assert common.repository(config, ALPHA)["siblings"] == ["beta: Drafts a release note."]


def test_the_repository_is_the_siblings_beside_the_skill_and_never_itself(workdir):
    """The directory above the skill is the repository; a sibling gives its one line, not its body."""
    config = common.Config()
    add_sibling(config, "beta", "Drafts a release note.")
    add_sibling(config, "gamma", "Trims the note down.")

    assert common.repository(config, ALPHA) == {
        "id": "owner-a/repo-a",
        "siblings": ["beta: Drafts a release note.", "gamma: Trims the note down."],
        "more": 0}


def test_a_repository_with_no_sibling_is_not_sent(workdir):
    """Nothing the skill's own name has not said, so no empty block is invented."""
    assert common.repository(common.Config(), ALPHA) is None


def test_a_sibling_with_no_description_is_named_without_one(workdir):
    """The slug is still a signal; a header nothing can be read from is not a reason to drop it."""
    config = common.Config()
    path = common.skill_md_path(config, ALPHA).parent.parent / "beta"
    path.mkdir()
    (path / common.SKILL_MD).write_text("Just a body.\n", encoding="utf-8")

    assert common.repository(config, ALPHA)["siblings"] == ["beta"]


def test_only_the_first_siblings_are_sent_and_the_rest_are_counted(workdir, monkeypatch):
    """A `awesome-*` collection cannot blow the request up: the cap holds and the rest are
    counted."""
    monkeypatch.setattr(common, "MAX_SIBLINGS", 1)
    config = common.Config()
    add_sibling(config, "beta", "First.")
    add_sibling(config, "gamma", "Second.")

    assert common.repository(config, ALPHA) == {
        "id": "owner-a/repo-a", "siblings": ["beta: First."], "more": 1}


def test_a_sibling_description_is_cut_to_a_hint(workdir):
    """A sibling's own description is sometimes a page: cut at a word so a repo of them cannot
    dwarf the skill's own body."""
    config = common.Config()
    add_sibling(config, "beta", "word " * 200)

    line = common.repository(config, ALPHA)["siblings"][0]

    assert line.startswith("beta: word word")
    assert line.endswith("…") and "  " not in line
    assert len(line) <= len("beta: ") + common.MAX_SIBLING_CHARS + 1


# ------------------------------------------------------------------------ prompts


def test_the_translation_prompts_are_two_files(config):
    """The chat angle's two turns live beside the domain state template, as Jinja templates, not
    prose in code: the system task carries {{to}}, the user turn carries {{to}} and {{text}}."""
    system = common.load_prompt(config, translate.PROMPT)
    user = common.load_prompt(config, translate.USER_PROMPT)

    assert "{{to}}" in system
    assert "{{to}}" in user and "{{text}}" in user
    assert not system.endswith("\n") and not user.endswith("\n")


# ------------------------------------------------------------------------- writes


def test_write_json_writes_one_object_renamed_into_place(config):
    path = common.profile_path(config, ALPHA, common.DOMAIN_ANGLE)
    written = common.write_json(path, {"domain": "testing", "confidence": 1.0})

    assert written == path
    assert written.read_text(encoding="utf-8") == '{"domain": "testing", "confidence": 1.0}'
    assert not path.with_name(path.name + ".part").exists()  # renamed into place


def test_an_atomic_write_keeps_the_previous_file_until_the_rename(config):
    path = config.output_dir / "catalog.txt"
    common.write_atomic(path, "first\n")
    common.write_atomic(path, "second\n")
    assert path.read_text(encoding="utf-8") == "second\n"
    assert not path.with_name(path.name + ".part").exists()


# ----------------------------------------------------------------------------- the call


def test_worth_retrying():
    """A dropped connection or a busy gateway is worth the next try; a rejected body is not."""
    request = httpx.Request("POST", common.DOMAIN_BASE_URL)
    assert common.worth_retrying(httpx.ReadTimeout("dropped"))
    for code in (429, 500, 502, 503, 504):
        error = httpx.HTTPStatusError("busy", request=request,
                                      response=httpx.Response(code, request=request))
        assert common.worth_retrying(error)
    error = httpx.HTTPStatusError("no", request=request,
                                  response=httpx.Response(400, request=request))
    assert not common.worth_retrying(error)


def test_a_dropped_call_is_retried(monkeypatch):
    """The endpoints regularly drop the first call after being idle, which arrives as a timeout:
    retrying keeps that from being recorded as a skill that could not be built."""
    calls = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            if len(calls) == 1:
                raise httpx.ReadTimeout("no response")
            return httpx.Response(200, json={"ok": True}, request=httpx.Request("POST", url))

    monkeypatch.setattr(common.time, "sleep", lambda seconds: None)

    assert common.post_json(Fake(), common.DOMAIN_BASE_URL, "k", {"q": 1}, max_retries=2) == {
        "ok": True}
    assert len(calls) == 2


def test_a_rejected_body_is_not_retried():
    calls = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            return httpx.Response(400, text="bad request", request=httpx.Request("POST", url))

    with pytest.raises(httpx.HTTPStatusError):
        common.post_json(Fake(), common.DOMAIN_BASE_URL, "k", {}, max_retries=3)
    assert len(calls) == 1
