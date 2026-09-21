"""gen.py: the prompt pair, the one call, and the two files it writes."""

import json
from pathlib import Path
from types import SimpleNamespace

import openai
import pytest

import gen

# the angles this script builds: `domain` is not one of them, being the System One endpoint's
ANGLES = {"blackbox", "comments", "scenario", "tagline", "whitebox"}
ALPHA = "owner-a/repo-a/alpha"


def scratch_prompts(tmp_path: Path, name: str, body: str,
                    schema: str | None = '{"type": "object"}') -> Path:
    """A scratch prompts dir with `_system.md` and one prompt pair.

    `schema=None` leaves the `.json` half out, which is how the tests reach the
    "a prompt is two files and both must be there" failures.
    """
    directory = tmp_path / "prompts"
    directory.mkdir(exist_ok=True)
    (directory / "_system.md").write_text(
        "<name>{{ name }}</name><description>{{ description }}</description>"
        "<skill_body>{{ skill_body }}</skill_body>", encoding="utf-8")
    (directory / f"{name}.md").write_text(body, encoding="utf-8")
    if schema is not None:
        (directory / f"{name}.json").write_text(schema, encoding="utf-8")
    return directory


def fake_client(monkeypatch, content: str = '{"text": "一句话介绍"}') -> dict:
    """Install a stand-in `openai.OpenAI`; returns what it recorded."""
    seen: dict = {}

    class Fake:
        def __init__(self, **kwargs):
            seen["built"] = kwargs
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        def create(self, *, model, messages, response_format=None, extra_body=None):
            """As narrow as the real one.

            `create()` raises TypeError on a keyword it does not have, so a fake that
            swallows anything lets the suite pass a call the SDK rejects - which is how a
            provider extension sent as a bare `chat_template_kwargs` shipped once.
            """
            seen["sent"] = {"model": model, "messages": messages,
                            "response_format": response_format}
            if extra_body is not None:
                seen["sent"]["extra_body"] = extra_body
            message = SimpleNamespace(content=content)
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    monkeypatch.setattr(openai, "OpenAI", Fake)
    return seen


# --------------------------------------------------------------- the prompt pair


def test_every_prompt_file_has_its_schema_next_to_it(config):
    """A prompt is a `<id>.md` + `<id>.json` pair, and neither half may be orphaned."""
    markdown = {path.name for path in config.prompts_dir.glob("*.md")}
    schemas = {path.name for path in config.prompts_dir.glob("*.json")}
    assert markdown == {f"{angle}.md" for angle in ANGLES} | {"_system.md"}
    assert schemas == {f"{angle}.json" for angle in ANGLES}


def test_load_prompt_reads_the_pair(config):
    template, schema = gen.load_prompt(config, "scenario")
    assert template.startswith("设想在一个场景下")
    assert schema["properties"]["text"]["type"] == "string"


def test_load_prompt_names_the_file_of_a_broken_template(tmp_path):
    config = gen.Config(prompts_dir=scratch_prompts(tmp_path, "broken", "{{ oops"))
    with pytest.raises(SystemExit, match="broken.md: invalid jinja2 template"):
        gen.load_prompt(config, "broken")


def test_load_prompt_rejects_a_schema_that_is_not_an_object(tmp_path):
    config = gen.Config(prompts_dir=scratch_prompts(
        tmp_path, "bad", "hi", schema='{"type": "array"}'))
    with pytest.raises(SystemExit, match="describing an object"):
        gen.load_prompt(config, "bad")


def test_load_prompt_reports_a_missing_schema(tmp_path):
    config = gen.Config(prompts_dir=scratch_prompts(tmp_path, "bad", "hi", schema=None))
    with pytest.raises(FileNotFoundError):
        gen.load_prompt(config, "bad")


def _check_strict(node: dict) -> None:
    """Strict mode closes every object and requires every field it declares: the
    provider enforces that, so a schema that breaks it gets a 400, not a retry."""
    if node.get("type") == "object":
        assert node.get("additionalProperties") is False
        assert set(node["required"]) == set(node["properties"])
        for child in node["properties"].values():
            _check_strict(child)
    if node.get("type") == "array":
        _check_strict(node["items"])


def test_every_schema_is_usable_in_strict_mode(config):
    for angle in ANGLES:
        _check_strict(gen.load_prompt(config, angle)[1])


def test_render_gives_the_template_the_body_the_description_and_the_name(config):
    """The three variables a system prompt may name, and nothing else."""
    assert gen.render("{{ skill_body }}!", "SOURCE", "ONE LINE", "AN ID") == "SOURCE!"
    assert gen.render("{{ description }}", "SOURCE", "ONE LINE", "AN ID") == "ONE LINE"
    assert gen.render("{{ name }}", "SOURCE", "ONE LINE", "AN ID") == "AN ID"
    assert gen.render("no variables here", "SOURCE", "ONE LINE", "AN ID") == "no variables here"


# ------------------------------------------------------------- the skill source


def test_a_short_source_is_passed_through_untouched(config):
    """No note, no reflow: the cap is the only thing that ever changes a source, and dropping the
    front matter is `skill_body`'s job rather than this one's."""
    source = gen.skill_source(config, ALPHA)
    assert source.startswith("---\nname: owner-a/repo-a/alpha\ndescription: Tidies a note list")
    assert source.endswith("---\n\nowner-a/repo-a/alpha does useful things.\n")


def test_the_sent_body_leaves_the_front_matter_behind(config):
    """The name and the description lead the message, so the copy of them at the top of the file
    is not sent a second time: the body starts at the first line that says something new."""
    body = gen.skill_body(gen.skill_source(config, ALPHA))

    assert body == "owner-a/repo-a/alpha does useful things.\n"


def test_a_source_with_no_front_matter_is_sent_as_it_is(workdir):
    """A file with nothing to drop is not a file to guess about, and a rule further down a body is
    not a header: the strip is anchored at the top, and what upstream wrote is what the model
    reads - a header arriving twice is not a failure, a body cut in half is."""
    text = "Just a body.\n\n---\n\nStill the body.\n"
    gen.skill_source_path(gen.Config(), ALPHA).write_text(text, encoding="utf-8")

    assert gen.skill_body(gen.skill_source(gen.Config(), ALPHA)) == text


# --------------------------------------------------------------- the description


def test_the_description_comes_from_the_skills_own_front_matter(config):
    """The index upstream publishes no longer carries one, so the file is the source."""
    assert gen.skill_description(gen.skill_source(config, ALPHA)).startswith("Tidies a note list")


def test_a_description_is_read_as_yaml_not_off_the_line(workdir):
    """A `description:` is a YAML value: `>` folds its lines and quotes unescape theirs, so what
    reaches the prompt is the text rather than the notation around it."""
    config = gen.Config()
    path = gen.skill_source_path(config, ALPHA)

    path.write_text("---\nname: alpha\ndescription: >-\n  Folds two lines\n  into one.\n---\n\nbody\n",
                    encoding="utf-8")
    assert gen.skill_description(gen.skill_source(config, ALPHA)) == "Folds two lines into one."

    path.write_text('---\nname: alpha\ndescription: "Says \\"hi\\" and stops."\n---\n\nbody\n',
                    encoding="utf-8")
    assert gen.skill_description(gen.skill_source(config, ALPHA)) == 'Says "hi" and stops.'


def test_a_skill_whose_front_matter_yields_no_description_is_dropped(workdir, capsys):
    """Nothing to lead a prompt with is nothing to build a profile from, so the skill is dropped
    - no call, no file - rather than answered from its body alone.

    The three ways to have nothing: no header at all, a header with no `description:` in it, and a
    header that is not YAML (`description: DEPRECATED: renamed elsewhere` - a bare colon and space
    is a mapping, and two skills in the current snapshot are written that way).
    """
    config = gen.Config()
    path = gen.skill_source_path(config, ALPHA)

    for text in ["Just a body, no header.\n",
                 "---\nname: alpha\n---\n\nA header with no description.\n",
                 "---\nname: alpha\ndescription: DEPRECATED: renamed elsewhere\n---\n\nBody.\n"]:
        path.write_text(text, encoding="utf-8")
        assert gen.skill_description(gen.skill_source(config, ALPHA)) == ""
        assert gen.main(["scenario", ALPHA]) == 1
        assert not gen.json_path(config, "scenario", ALPHA).exists()
        assert "no description in its front matter" in capsys.readouterr().err


def test_a_long_source_is_cut_on_a_line_break_and_says_so(workdir):
    """Both halves, because either alone is a bug.

    Mid-line would hand over a heading or a table in half; silent would read as a source
    that simply ended, which is how an answer ends up confident about the part nobody
    sent. About one skill in ten is long enough to reach this.
    """
    config = gen.Config()
    body = "".join(f"line {i:04d} " + "x" * 40 + "\n" for i in range(500))
    assert len(body) > gen.MAX_SKILL_MD_CHARS
    gen.skill_source_path(config, ALPHA).write_text(body, encoding="utf-8")

    source = gen.skill_source(config, ALPHA)

    head = source.removesuffix(f"\n\n{gen.TRUNCATION_NOTE}\n")
    assert head != source  # the note is there, at the end
    assert len(source) < len(body)  # and something really was dropped
    assert len(head) <= gen.MAX_SKILL_MD_CHARS  # never past the budget
    assert body.startswith(head + "\n")  # a prefix of the file, ending at a line end
    assert all(line.startswith("line ") for line in head.splitlines())  # whole lines only


# ------------------------------------------------------------------- the call


def test_dry_run_returns_a_placeholder_shaped_like_the_schema(config):
    """Objects and arrays come out shaped right, with no per-prompt fake to write."""
    assert gen.call(config, gen.load_prompt(config, "blackbox")[1], []) == {
        "function": "离线演示占位内容",
        "input_output": [{"input": "离线演示占位内容", "output": "离线演示占位内容"}],
    }


def test_call_sends_the_prompt_schema_as_the_response_format(workdir, monkeypatch):
    """The schema the provider decodes against is the prompt file's own: there is no
    second copy of an output's shape anywhere in the code."""
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    monkeypatch.setenv("SKILLS_PROFILES_MAX_RETRIES", "7")
    seen = fake_client(monkeypatch)
    config = gen.Config()
    schema = gen.load_prompt(config, "scenario")[1]

    assert gen.call(config, schema, [{"role": "user", "content": "hi"}]) == {"text": "一句话介绍"}

    assert seen["sent"]["response_format"] == {
        "type": "json_schema",
        "json_schema": {"name": "profile", "strict": True, "schema": schema}}
    # only keywords create() accepts: the retry budget lives on the client, and one
    # stray keyword is a TypeError on the first real request
    assert set(seen["sent"]) == {"model", "messages", "response_format"}
    assert seen["built"]["max_retries"] == 7


def test_thinking_is_opt_in_and_sends_only_the_provider_flag(workdir, monkeypatch):
    """Reasoning is a provider extension, so it is the one thing that changes the wire
    format - and only when asked for.

    Pinned because it cannot be checked against the docs: they document `true` and say
    nothing about `false`, so the flag is sent when switching on and never otherwise. It
    was confirmed by hand against apihub.agnes-ai.com with `agnes-3.0-flash`, where the
    request comes back with `reasoning_content` beside a `content` that is still strict
    json - which is what makes it safe to combine with the response format below.
    """
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    monkeypatch.setenv("SKILLS_PROFILES_THINKING", "1")
    seen = fake_client(monkeypatch)
    config = gen.Config()
    assert config.thinking is True

    gen.call(config, gen.load_prompt(config, "scenario")[1],
             [{"role": "user", "content": "hi"}])

    # under `extra_body`, because `create()` has no `chat_template_kwargs` parameter and
    # raises TypeError on one: the field reaches the endpoint, the keyword would not
    assert seen["sent"]["extra_body"] == {"chat_template_kwargs": {"enable_thinking": True}}
    assert set(seen["sent"]) == {"model", "messages", "response_format", "extra_body"}


def test_call_rejects_an_empty_answer(workdir, monkeypatch):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    fake_client(monkeypatch, content="")
    with pytest.raises(RuntimeError, match="empty message"):
        gen.call(gen.Config(), {"type": "object"}, [])


# ------------------------------------------------------------------ the outputs


def test_write_writes_json_and_the_markdown_copy(config):
    path = gen.write(config, "scenario", ALPHA, {"text": "一句话介绍"})
    assert path == gen.json_path(config, "scenario", ALPHA)
    assert json.loads(path.read_text(encoding="utf-8")) == {"text": "一句话介绍"}
    markdown = gen.markdown_path(config, "scenario", ALPHA).read_text(encoding="utf-8")
    assert markdown.startswith(f"# alpha (`{ALPHA}`)\n\n## scenario\n")
    assert "### text\n\n一句话介绍" in markdown


def test_markdown_labels_every_field(config):
    """Two list fields in one schema must not render as two unlabelled groups."""
    markdown = gen._markdown("whitebox", ALPHA, {
        "function": "一句话",
        "execution_flow": ["步骤一"],
        "input_output": [{"input": "a.md", "output": "a.pdf"}],
    })
    assert "- input: a.md, output: a.pdf" in markdown
    assert "### execution_flow\n\n- 步骤一" in markdown
    assert "### function\n\n一句话" in markdown


# ---------------------------------------------------------------------- main


def test_main_writes_one_output(config):
    assert gen.main(["scenario", ALPHA]) == 0
    assert gen.json_path(config, "scenario", ALPHA).is_file()
    assert gen.markdown_path(config, "scenario", ALPHA).is_file()


def test_main_passes_the_source_and_the_task(workdir, monkeypatch):
    seen: dict = {}

    def capture(config, schema, messages):
        seen["messages"] = messages
        seen["schema"] = schema
        return gen._placeholder(schema)

    monkeypatch.setattr(gen, "call", capture)
    assert gen.main(["scenario", ALPHA]) == 0

    system, user = seen["messages"]
    assert system["role"] == "system"
    assert "先读 description" in system["content"]
    assert f"<name>\n{ALPHA}\n</name>" in system["content"]  # the handle the tree calls it by
    assert "Tidies a note list" in system["content"]  # the skill's own one line
    assert f"{ALPHA} does useful things." in system["content"]  # and the body under it
    assert "name: owner-a/repo-a/alpha" not in system["content"]  # said once, not twice
    assert user["role"] == "user" and "设想在一个场景下" in user["content"]
    assert seen["schema"] == gen.load_prompt(gen.Config(), "scenario")[1]


@pytest.mark.parametrize("variable", ["skill_body", "description", "name"])
def test_a_task_template_cannot_ask_for_a_system_variable(workdir, monkeypatch, tmp_path, variable):
    """The name, the description and the body reach the system message only, so a task template
    that names one is an error when it is loaded - not an empty string when it is called."""
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    real = gen.Config().prompts_dir
    (prompts / "scenario.json").write_text((real / "scenario.json").read_text(), encoding="utf-8")
    (prompts / "scenario.md").write_text(f"{{{{ {variable} }}}}", encoding="utf-8")
    monkeypatch.setenv("SKILLS_PROFILES_PROMPTS_DIR", str(prompts))

    with pytest.raises(SystemExit, match="is undefined"):
        gen.load_prompt(gen.Config(), "scenario")


def test_a_system_prompt_that_names_an_unknown_variable_is_a_message(workdir, monkeypatch,
                                                                    tmp_path, capsys):
    """`_system.md` is the one template rendered with variables, so a name it does not have is
    answered with the file it is in rather than a traceback out of the run."""
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    real = gen.Config().prompts_dir
    for name in ("_system.md", "scenario.md", "scenario.json"):
        (prompts / name).write_text((real / name).read_text(encoding="utf-8"), encoding="utf-8")
    (prompts / "_system.md").write_text("{{ nosuchvar }}", encoding="utf-8")
    monkeypatch.setenv("SKILLS_PROFILES_PROMPTS_DIR", str(prompts))

    assert gen.main(["scenario", ALPHA]) == 1

    assert "_system.md: 'nosuchvar' is undefined" in capsys.readouterr().err


def test_print_shows_the_request_and_calls_nothing(workdir, monkeypatch, capsys):
    """`--print` answers a question rather than doing work: it is how you see exactly what a
    prompt sends, so it must not spend a call or leave a file behind."""
    def explode(*args, **kwargs):
        raise AssertionError("the model was called")

    monkeypatch.setattr(gen, "call", explode)
    assert gen.main(["scenario", ALPHA, "--print"]) == 0

    out = capsys.readouterr().out
    assert "----- system -----" in out and "does useful things." in out
    assert "----- user -----" in out
    assert not gen.json_path(gen.Config(), "scenario", ALPHA).exists()


def test_a_missing_input_is_a_message_not_a_traceback(workdir, capsys):
    """A prompt or a skill that is not there is the caller's typo to fix, so it exits 1 with
    the path - the same way a bad schema does, and never as a traceback."""
    assert gen.main(["domain", "owner-a/repo-a/nope"]) == 1
    assert "not found" in capsys.readouterr().err

    assert gen.main(["nosuchangle", ALPHA]) == 1
    assert "not found" in capsys.readouterr().err
