#!/usr/bin/env python3
"""The chat endpoint the zh page angle asks: one free-text turn, Chinese out.

Where `jev.py` asks the typed System One endpoint a closed question, this is the OpenAI-compatible
chat endpoint `skill_zh.py` asks once for the one-line description and then once per body piece.
The description turns are rendered from `prompts/translate.md` and `prompts/translate_user.md`;
the body pieces carry their own prompts beside them.

The default endpoint is Xunfei Xingchen MaaS serving Spark-X2.5-4B; base url and model are
overridable, because the model id is what the console's service page shows for the subscription.
A call the endpoint fails is retried once on a fallback endpoint - Agnes AI by default, its
address, model and key under the `TRANSLATE_FALLBACK_*` settings.

A library rather than a command: the justfile drives `skill_zh.py`, one process per skill.
"""

import sys

import httpx

import common
from common import Config

# The two prompts, beside the domain state template: the system task and the one user turn.
PROMPT = "translate.md"
USER_PROMPT = "translate_user.md"
# The one target language both templates are rendered with; the catalog is a Chinese description of
# each skill, and the value is the language as it is named in the prompt itself.
TO = "Simplified Chinese (简体中文)"


def turns(config: Config, text: str, system_prompt: str, user_prompt: str) -> list[dict]:
    """One chat turn: the task rendered for the target language, then the text to render into it -
    and nothing else.

    The text goes in as a template variable rather than text of the template, so braces in a
    skill's own words can never be read as Jinja. The two prompt files are the caller's, so the
    description and the body pieces share this one renderer.
    """
    system = common.render(common.load_prompt(config, system_prompt), to=TO)
    user = common.render(common.load_prompt(config, user_prompt), to=TO, text=text)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def chat_body(config: Config, messages: list[dict]) -> dict:
    """An OpenAI-compatible chat completions body over the turns given: deterministic,
    non-streaming.

    `enable_thinking` is the MaaS extension (a top-level body field, `extra_body` in the OpenAI
    SDK): the model reasons into `reasoning_content` first, and `max_tokens` covers thinking plus
    the answer, so it is the ceiling the endpoint documents rather than its 2048 default.
    """
    body = {"model": config.translate_model, "messages": messages,
            "temperature": 0, "stream": False, "max_tokens": config.translate_max_tokens}
    if config.translate_enable_thinking:
        body["enable_thinking"] = True
    return body


def request_body(config: Config, description: str) -> dict:
    """The one request the description needs: the two prompt files this library holds."""
    return chat_body(config, turns(config, description, PROMPT, USER_PROMPT))


def translation(payload: object) -> str:
    """The answer text out of a chat completion payload; a body without one is a failed call.

    The endpoint answers 200 with an empty `content` when it has nothing to say, which would
    otherwise write an empty translation the batch would trust as done. A `finish_reason` of
    `length` means the token budget cut the answer mid-document: that half translation is
    unusable input too, because a file is whole or absent.
    """
    choices = payload.get("choices") if isinstance(payload, dict) else None
    first = choices[0] if isinstance(choices, list) and choices else None
    if isinstance(first, dict) and first.get("finish_reason") == "length":
        raise RuntimeError("answer hit the token budget - translation truncated")
    message = first.get("message") if isinstance(first, dict) else None
    text = message.get("content") if isinstance(message, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("response carries no translation")
    return text.strip()


class Translator:
    """One `POST /chat/completions`: one line in, its Chinese translation out.

    The primary endpoint answers first; a skill it fails outright is asked once more on the
    fallback endpoint, a different model behind the same OpenAI protocol.
    """

    def __init__(self, config: Config, client: httpx.Client | None = None):
        key = config.translate_api_key
        if not key:
            raise SystemExit(
                "SKILLS_PROFILES_TRANSLATE_API_KEY is not set - nothing to call with")
        self.config = config
        self.api_key = key
        self.fallback_api_key = config.translate_fallback_api_key
        self.client = client or httpx.Client(timeout=config.timeout)

    def _chat_url(self, base_url: str) -> str:
        """The base joined with the chat path once, so a trailing slash in an override is harmless."""
        return f"{base_url.rstrip('/')}/chat/completions"

    @property
    def url(self) -> str:
        return self._chat_url(self.config.translate_base_url)

    @property
    def fallback_url(self) -> str:
        return self._chat_url(self.config.translate_fallback_base_url)

    def ask(self, body: dict) -> str:
        """The one call; a primary that fails the skill hands it to the fallback endpoint once.

        Anything the primary raises after its own retries - a dropped call, a rejected body, an
        empty or truncated answer - is worth one try elsewhere, because a different model may
        take the input it choked on. The request travels as built with only the model swapped;
        the fallback's own failure raises as itself, so a skill both endpoints fail is still one
        diagnosable error, and no fallback key means the primary error stands unchanged.
        """
        try:
            return translation(common.post_json(
                self.client, self.url, self.api_key, body, self.config.max_retries))
        except (httpx.HTTPError, RuntimeError) as error:
            if not self.fallback_api_key:
                raise
            print(f"primary translate endpoint failed ({type(error).__name__}); "
                  f"retrying on {self.config.translate_fallback_model}", file=sys.stderr)
            return translation(common.post_json(
                self.client, self.fallback_url, self.fallback_api_key,
                {**body, "model": self.config.translate_fallback_model},
                self.config.max_retries))
