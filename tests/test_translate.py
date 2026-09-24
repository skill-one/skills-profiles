"""translate.py: the one skill in, one line translated, one description_zh.json written.

Offline like test_jev: the chat endpoint is a stand-in client, and everything the command does
short of the call - the source reading, the request messages, the layout, the gate, the exit
codes - runs for real.
"""

import json

import httpx
import pytest

import common
import translate

ALPHA = "owner-a/repo-a/alpha"
ZH = "整理笔记列表，把零散的头绪折进一份持续更新的索引，并让整堆内容可搜索。"


class FakeTranslator:
    """A stand-in endpoint: one fixed Chinese line, or whatever the test wants to see fail."""

    def __init__(self, config, client=None):
        pass

    def ask(self, body: dict) -> str:
        return ZH


# ------------------------------------------------------------------ the request


def test_the_request_is_one_chat_turn(config):
    """The OpenAI shape: a system instruction and the one user line, deterministic and
    non-streaming - and nothing else an answer could drift on. Both turns are the prompt files
    rendered for the one target language."""
    description = "Tidies a note list."
    body = translate.request_body(config, description)
    system = common.render(common.load_prompt(config, translate.PROMPT), to=translate.TO)
    user = common.render(common.load_prompt(config, translate.USER_PROMPT),
                         to=translate.TO, text=description)

    assert body == {
        "model": common.TRANSLATE_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "stream": False,
        "max_tokens": 32768,
        "enable_thinking": True,
    }
    assert "简体中文" in system  # {{to}} rendered, in both turns
    assert "{{" not in system and "{{" not in user
    assert user.endswith(description)
    assert "Preserve its meaning" in system


def test_thinking_can_be_switched_off():
    """Deep thinking is the default, but a plain call must be one flag away - and the token budget
    is still there, so an answer is never cut at the endpoint's own 2048 default."""
    off = translate.request_body(
        common.Config(translate_enable_thinking=False), "hi")

    assert "enable_thinking" not in off
    assert off["max_tokens"] == 32768


def test_braces_in_a_description_are_data_not_template(config):
    """The description is a Jinja *value*, not part of the template: braces a skill writes in its
    own line are sent as written and can never trip the renderer."""
    description = "Use {{placeholder}} and {x} as written."
    body = translate.request_body(config, description)

    user = body["messages"][1]["content"]
    assert user.endswith(description)
    assert "{{placeholder}}" in user


def test_print_sends_the_messages_and_calls_nothing(workdir, capsys):
    """Printed from `workdir`, where there is no `.env`: a request that needs no key is the point
    of `just translate-render`."""
    assert translate.main(["--print", ALPHA]) == 0
    body = json.loads(capsys.readouterr().out)

    assert body["model"] == common.TRANSLATE_MODEL
    assert [m["role"] for m in body["messages"]] == ["system", "user"]
    user = body["messages"][1]["content"]
    assert user.startswith(f"Translate to {translate.TO}:")
    assert "Tidies a note list" in user  # the line to translate, carried by the user template


def test_the_translate_endpoint_is_configurable(workdir, monkeypatch):
    """The base url and model id are the console's, so a run overrides them through the same
    prefixed environment as everything else."""
    monkeypatch.setenv("SKILLS_PROFILES_TRANSLATE_BASE_URL", "https://example.test/v2")
    monkeypatch.setenv("SKILLS_PROFILES_TRANSLATE_MODEL", "other-model")

    config = common.Config()

    assert config.translate_base_url == "https://example.test/v2"
    assert config.translate_model == "other-model"


# -------------------------------------------------------------------- the call


def completion(content: str = ZH) -> httpx.Response:
    return httpx.Response(
        200, json={"choices": [{"message": {"role": "assistant", "content": content}}]},
        request=httpx.Request("POST", common.TRANSLATE_BASE_URL))


def test_ask_posts_one_chat_completion(config):
    seen: dict = {}

    class Fake:
        def post(self, url, headers=None, json=None):
            seen.update({"url": url, "headers": headers, "json": json})
            return completion()

    client = translate.Translator(
        common.Config(translate_api_key="k"), client=Fake())
    answer = client.ask(translate.request_body(config, "hi"))

    assert answer == ZH
    assert seen["url"] == "https://maas-api.cn-huabei-1.xf-yun.com/v2/chat/completions"
    assert seen["headers"] == {"Authorization": "Bearer k"}
    assert seen["json"]["messages"][-1]["content"] == (
        f"Translate to {translate.TO}:\n\nhi")


def test_the_base_url_is_joined_without_a_double_slash():
    """A trailing slash in an override is the reader's to add or not; the path is joined once."""
    seen: dict = {}

    class Fake:
        def post(self, url, headers=None, json=None):
            seen["url"] = url
            return completion()

    config = common.Config(translate_api_key="k",
                           translate_base_url="https://example.test/v2/")
    translate.Translator(config, client=Fake()).ask({})

    assert seen["url"] == "https://example.test/v2/chat/completions"


def test_a_dropped_call_is_retried(monkeypatch):
    """Same reading as the domain endpoint: a dropped first call arrives as a timeout and is
    retried rather than recorded as a skill that could not be translated."""
    calls = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            if len(calls) == 1:
                raise httpx.ReadTimeout("no response")
            return completion()

    monkeypatch.setattr(common.time, "sleep", lambda seconds: None)
    client = translate.Translator(
        common.Config(translate_api_key="k", max_retries=2), client=Fake())

    assert client.ask({}) == ZH
    assert len(calls) == 2


def test_a_rejected_body_is_not_retried():
    calls = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            return httpx.Response(400, text="bad request",
                                  request=httpx.Request("POST", url))

    client = translate.Translator(
        common.Config(translate_api_key="k", max_retries=3), client=Fake())
    with pytest.raises(httpx.HTTPStatusError):
        client.ask({})
    assert len(calls) == 1


def test_a_malformed_json_response_is_named_as_a_failure():
    """A 200 with a non-JSON body must become a diagnosable failure, not an unclassified decode
    traceback."""
    class Fake:
        def post(self, url, headers=None, json=None):
            return httpx.Response(200, content=b"not json",
                                  request=httpx.Request("POST", url))

    client = translate.Translator(common.Config(translate_api_key="k"), client=Fake())
    with pytest.raises(RuntimeError, match="not valid JSON"):
        client.ask({})


def test_an_empty_answer_is_a_failure():
    """A 200 with no text would otherwise write an empty translation the batch would trust as
    done: it is a failed call instead, so nothing is written and the run retries it."""
    payloads = [
        {},
        {"choices": []},
        {"choices": [{}]},
        {"choices": [{"message": {}}]},
        {"choices": [{"message": {"content": "  "}}]},
    ]
    for payload in payloads:
        with pytest.raises(RuntimeError, match="no translation"):
            translate.translation(payload)
    assert translate.translation({"choices": [{"message": {"content": f"  {ZH}  "}}]}) == ZH


def test_the_reasoning_is_read_around_not_as_the_answer():
    """With thinking on, the same message carries `reasoning_content` too: it is the model's draft,
    and the translation is still `content` alone - trimmed, the thinking never written to disk."""
    payload = {"choices": [{"message": {
        "reasoning_content": "First I parse the sentence... (draft)",
        "content": f" {ZH} "}}]}

    assert translate.translation(payload) == ZH


def test_no_key_is_no_call(workdir, monkeypatch):
    """A key in the developer's environment cannot answer for one that is not in `.env`."""
    monkeypatch.delenv("SKILLS_PROFILES_TRANSLATE_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="SKILLS_PROFILES_TRANSLATE_API_KEY"):
        translate.Translator(common.Config())


# ------------------------------------------------------------------ the output


def test_the_angle_file_sits_beside_the_domain_file(config):
    """The two angles on one skill share its profile directory."""
    path = common.write_json(
        common.profile_path(config, ALPHA, common.TRANSLATE_ANGLE),
        {common.TRANSLATE_ANGLE: ZH})

    assert path == common.profile_path(config, ALPHA, common.TRANSLATE_ANGLE)
    assert json.loads(path.read_text(encoding="utf-8")) == {"description_zh": ZH}
    assert not path.with_name(path.name + ".part").exists()  # renamed into place
    assert path.parent == common.profile_dir(config, ALPHA)  # beside domain.json, in the same dir


# ---------------------------------------------------------------------- main


def test_a_dry_run_writes_the_layout_without_calling(config):
    """`just dry=1 translate` is offline, and the tree it leaves is the tree a real run leaves."""
    assert translate.main([ALPHA]) == 0

    written = json.loads(common.profile_path(
        config, ALPHA, common.TRANSLATE_ANGLE).read_text(encoding="utf-8"))
    assert list(written) == ["description_zh"]
    assert written["description_zh"].startswith("【占位】")  # identifiable as a placeholder
    assert written["description_zh"].endswith("the whole pile searchable.")  # the line it faked


def test_main_writes_one_output(workdir, monkeypatch):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")
    monkeypatch.setattr(translate, "Translator", FakeTranslator)
    config = common.Config()

    assert translate.main([ALPHA]) == 0

    assert json.loads(common.profile_path(
        config, ALPHA, common.TRANSLATE_ANGLE).read_text(encoding="utf-8")) == {
        "description_zh": ZH}


def test_a_call_that_fails_is_one_line_and_status_one(workdir, monkeypatch, capsys):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")

    class Broken:
        def __init__(self, config, client=None):
            pass

        def ask(self, body: dict) -> str:
            raise httpx.ReadTimeout("dropped")

    monkeypatch.setattr(translate, "Translator", Broken)

    assert translate.main([ALPHA]) == 1
    assert not common.profile_path(common.Config(), ALPHA, common.TRANSLATE_ANGLE).exists()
    assert "ReadTimeout" in capsys.readouterr().err


def test_an_empty_answer_fails_the_command(workdir, monkeypatch, capsys):
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "0")

    class Empty:
        def __init__(self, config, client=None):
            pass

        def ask(self, body: dict) -> str:
            raise RuntimeError("response carries no translation")

    monkeypatch.setattr(translate, "Translator", Empty)

    assert translate.main([ALPHA]) == 1
    assert not common.profile_path(common.Config(), ALPHA, common.TRANSLATE_ANGLE).exists()
    assert "RuntimeError" in capsys.readouterr().err


def test_a_skill_whose_front_matter_yields_no_description_is_dropped(workdir, capsys):
    """The same gate as jev.py: nothing to translate is nothing to call."""
    config = common.Config()
    path = common.skill_md_path(config, ALPHA)
    path.write_text("---\nname: alpha\n---\n\nA header with no description.\n", encoding="utf-8")

    assert translate.main([ALPHA]) == 1
    assert not common.profile_path(config, ALPHA, common.TRANSLATE_ANGLE).exists()
    assert "no description in its front matter" in capsys.readouterr().err


def test_a_missing_skill_is_a_message_not_a_traceback(workdir, capsys):
    assert translate.main(["owner-a/repo-a/nope"]) == 1
    assert "not found" in capsys.readouterr().err


def test_bad_arguments_are_status_two(capsys):
    assert translate.main([]) == 2
    assert "usage: translate.py" in capsys.readouterr().err
