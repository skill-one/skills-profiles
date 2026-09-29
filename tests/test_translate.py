"""translate.py: the chat endpoint library the zh page angle asks per page - description and pieces.

Offline like test_jev: the endpoint is a stand-in client, and everything the library does short
of the call - the request messages, the answer parsing, the fallback hand-over - runs for real.
"""

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
    assert off["max_tokens"] > 2048


def test_braces_in_a_description_are_data_not_template(config):
    """The description is a Jinja *value*, not part of the template: braces a skill writes in its
    own line are sent as written and can never trip the renderer."""
    description = "Use {{placeholder}} and {x} as written."
    body = translate.request_body(config, description)

    user = body["messages"][1]["content"]
    assert user.endswith(description)
    assert "{{placeholder}}" in user


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

    # the fallback key is pinned off: this test is about the primary's own retries, and a local
    # `.env` that arms the fallback must not turn it into a fallback test
    client = translate.Translator(
        common.Config(translate_api_key="k", translate_fallback_api_key=None, max_retries=3),
        client=Fake())
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


def test_a_truncated_answer_is_a_failure():
    """`finish_reason=length` means the budget cut the document mid-way: a half translation is
    unusable input, not a file the batch would trust as done."""
    payload = {"choices": [{"finish_reason": "length", "message": {"content": "半截译文"}}]}
    with pytest.raises(RuntimeError, match="truncated"):
        translate.translation(payload)


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


# ---------------------------------------------------------------- the fallback


def fallback_config(**overrides) -> common.Config:
    return common.Config(
        translate_api_key="k", translate_fallback_api_key="fk", **overrides)


def test_a_rejected_body_is_asked_once_on_the_fallback(capsys):
    """The second model is the second chance: a skill the primary fails outright - here a
    rejected body - is tried once on the fallback endpoint, the same request with only the
    model swapped in."""
    seen: list[dict] = []

    class Fake:
        def post(self, url, headers=None, json=None):
            seen.append({"url": url, "headers": headers, "json": json})
            if len(seen) == 1:
                return httpx.Response(400, text="bad request",
                                      request=httpx.Request("POST", url))
            return completion()

    config = fallback_config(translate_fallback_base_url="https://example.test/v1/",
                             translate_fallback_model="other-model")
    body = translate.request_body(config, "hi")

    def chat_url(base: str) -> str:
        return f"{base.rstrip('/')}/chat/completions"

    assert translate.Translator(config, client=Fake()).ask(body) == ZH
    assert [c["url"] for c in seen] == [
        chat_url(config.translate_base_url), "https://example.test/v1/chat/completions"]
    assert seen[1]["headers"] == {"Authorization": "Bearer fk"}
    assert seen[1]["json"] == {**body, "model": "other-model"}
    assert "retrying on other-model" in capsys.readouterr().err


def test_an_empty_answer_is_also_handed_to_the_fallback():
    """A 200 that carries no translation fails the primary like any other answer, and the
    fallback gets its turn at the same skill."""
    calls: list[str] = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            if len(calls) == 1:
                return completion(content="  ")
            return completion()

    config = fallback_config()
    assert translate.Translator(config, client=Fake()).ask({}) == ZH
    assert len(calls) == 2


def test_without_a_fallback_key_the_primary_error_stands():
    """No second key, no second try: the failure is the primary's, exactly as before. The key
    is pinned off in the constructor, so a local `.env` that arms the fallback cannot."""
    calls: list[str] = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            return httpx.Response(400, text="bad request",
                                  request=httpx.Request("POST", url))

    config = common.Config(translate_api_key="k", translate_fallback_api_key=None)
    with pytest.raises(httpx.HTTPStatusError):
        translate.Translator(config, client=Fake()).ask({})
    assert len(calls) == 1


def test_a_failing_fallback_raises_as_itself():
    """A skill both endpoints fail is one failure: the last error answers, unswallowed."""
    calls: list[str] = []

    class Fake:
        def post(self, url, headers=None, json=None):
            calls.append(url)
            return httpx.Response(400, text="bad request",
                                  request=httpx.Request("POST", url))

    with pytest.raises(httpx.HTTPStatusError):
        translate.Translator(fallback_config(), client=Fake()).ask({})
    assert len(calls) == 2


def test_the_fallback_endpoint_is_configurable(workdir, monkeypatch):
    """The same prefixed environment as everything else: the Agnes defaults are code, the
    deployment's spelling is configuration."""
    monkeypatch.setenv("SKILLS_PROFILES_TRANSLATE_FALLBACK_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("SKILLS_PROFILES_TRANSLATE_FALLBACK_MODEL", "other-model")
    monkeypatch.delenv("SKILLS_PROFILES_TRANSLATE_FALLBACK_API_KEY", raising=False)

    config = common.Config()

    assert config.translate_fallback_base_url == "https://example.test/v1"
    assert config.translate_fallback_model == "other-model"
    assert config.translate_fallback_api_key is None  # unset means unset - no fallback key
