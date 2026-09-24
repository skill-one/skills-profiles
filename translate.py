#!/usr/bin/env python3
"""Translate one skill's description into Simplified Chinese, over an OpenAI-compatible chat API.

The second angle on a skill. Where `jev.py` asks the typed System One endpoint a closed question,
this asks a chat completions endpoint one free-text question: the skill's own one-line description
in, Chinese out. Its two turns are rendered from `prompts/translate.md` and
`prompts/translate_user.md`; the layout, the gate and the contract are the shared command in
`common.py`.

    translate.py <skill> [--print]   translate one skill, or print the request and call nothing

The default endpoint is Xunfei Xingchen MaaS serving Spark-X2.5-4B; base url and model are
overridable, because the model id is what the console's service page shows for the subscription.

Driven by the justfile, one process per skill.
"""

import httpx

import common
from common import Config

# The two prompts, beside the domain state template: the system task and the one user turn.
PROMPT = "translate.md"
USER_PROMPT = "translate_user.md"
# The one target language both templates are rendered with; the catalog is a Chinese description of
# each skill, and the value is the language as it is named in the prompt itself.
TO = "Simplified Chinese (简体中文)"


def messages(config: Config, description: str) -> list[dict]:
    """The one chat turn: the task rendered for the target language, then the one line to render
    into it - and nothing else.

    The description goes in as a template variable rather than text of the template, so braces in a
    skill's own words can never be read as Jinja.
    """
    system = common.render(common.load_prompt(config, PROMPT), to=TO)
    user = common.render(common.load_prompt(config, USER_PROMPT), to=TO, text=description)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def chat_body(config: Config, turns: list[dict]) -> dict:
    """An OpenAI-compatible chat completions body over the turns given: deterministic,
    non-streaming.

    `enable_thinking` is the MaaS extension (a top-level body field, `extra_body` in the OpenAI
    SDK): the model reasons into `reasoning_content` first, and `max_tokens` covers thinking plus
    the answer, so it is the ceiling the endpoint documents rather than its 2048 default.
    """
    body = {"model": config.translate_model, "messages": turns,
            "temperature": 0, "stream": False, "max_tokens": config.translate_max_tokens}
    if config.translate_enable_thinking:
        body["enable_thinking"] = True
    return body


def request_body(config: Config, description: str) -> dict:
    return chat_body(config, messages(config, description))


def translation(payload: object) -> str:
    """The answer text out of a chat completion payload; a body without one is a failed call.

    The endpoint answers 200 with an empty `content` when it has nothing to say, which would
    otherwise write an empty translation the batch would trust as done.
    """
    choices = payload.get("choices") if isinstance(payload, dict) else None
    first = choices[0] if isinstance(choices, list) and choices else None
    message = first.get("message") if isinstance(first, dict) else None
    text = message.get("content") if isinstance(message, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("response carries no translation")
    return text.strip()


class Translator:
    """One `POST /chat/completions`: one line in, its Chinese translation out."""

    def __init__(self, config: Config, client: httpx.Client | None = None):
        key = config.translate_api_key
        if not key:
            raise SystemExit(
                "SKILLS_PROFILES_TRANSLATE_API_KEY is not set - nothing to call with")
        self.config = config
        self.api_key = key
        self.client = client or httpx.Client(timeout=config.timeout)

    @property
    def url(self) -> str:
        """The base joined with the chat path once, so a trailing slash in an override is harmless."""
        return f"{self.config.translate_base_url.rstrip('/')}/chat/completions"

    def ask(self, body: dict) -> str:
        """The one call; an empty answer is raised as a bad endpoint, not an empty translation."""
        return translation(common.post_json(
            self.client, self.url, self.api_key, body, self.config.max_retries))


def placeholder(description: str) -> dict:
    """A value shaped like the answer, so `just dry=1 translate` still writes the real layout."""
    return {common.TRANSLATE_ANGLE: f"【占位】{description}"}


def _request(config: Config, _skill: str, _source: str, description: str) -> dict:
    return request_body(config, description)


def _produce(config: Config, body: dict, _source: str) -> dict:
    return {common.TRANSLATE_ANGLE: Translator(config).ask(body)}


def main(argv: list[str] | None = None) -> int:
    return common.run(
        argv, program="translate.py",
        description="Translate one skill's description into Chinese.",
        angle=common.TRANSLATE_ANGLE, build_request=_request, produce=_produce,
        placeholder=placeholder)


if __name__ == "__main__":
    raise SystemExit(main())
