#!/usr/bin/env python3
"""Translate one skill's SKILL.md body into Simplified Chinese, over the same chat API.

The third angle on a skill, beside domain.json and description_zh.json: the body of the skill's
own page in, its Chinese translation out. Only the translation is written - the page is not an
installation, and the identifying metadata (name, description) already lives in the catalog and
the other two angle files.

    skill_zh.py <skill> [--print]   translate one skill, or print the request and call nothing

A body past MAX_BODY_CHARS is unusable input, like a missing description: nothing is written,
because a half-translated page must never pass for a whole one.

The two turns are rendered from `prompts/skill_zh.md` and `prompts/skill_zh_user.md`; the
endpoint, the layout, the gate and the contract are the ones `translate.py` and `common.py`
already hold.

Driven by the justfile, one process per skill.
"""

import common
import translate
from common import Config

# The two prompts, beside the other angles': the system task and the one user turn.
PROMPT = "skill_zh.md"
USER_PROMPT = "skill_zh_user.md"
# The one target language the templates are rendered with; the value is the language as it is
# named in the prompt itself.
TO = "Simplified Chinese (简体中文)"
# A body past this is not translated: the endpoint cannot take it whole, and a truncated page
# would be a half answer written as a whole one.
MAX_BODY_CHARS = 60000


def messages(config: Config, body_text: str) -> list[dict]:
    """The one chat turn: the task rendered for the target language, then the body to render
    into it - and nothing else.

    The body goes in as a template variable rather than text of the template, so braces in a
    skill's own words can never be read as Jinja.
    """
    system = common.render(common.load_prompt(config, PROMPT), to=TO)
    user = common.render(common.load_prompt(config, USER_PROMPT), to=TO, text=body_text)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _request(config: Config, skill: str, source: str, _description: str) -> dict:
    """The chat body for the skill's own body - and the one gate the angle adds: a body too long
    for the endpoint, or an empty one, is dropped here before any call."""
    body_text = common.skill_body(source)
    if not body_text.strip() or len(body_text) > MAX_BODY_CHARS:
        raise SystemExit(
            f"{skill}: body is empty or over {MAX_BODY_CHARS} characters - not translated")
    return translate.chat_body(config, messages(config, body_text))


def _produce(config: Config, body: dict, _source: str) -> str:
    """The one Chinese page: the translation alone."""
    return f"{translate.Translator(config).ask(body).strip()}\n"


def placeholder(description: str) -> str:
    """A value shaped like the answer, so `just dry=1 skill-zh` still writes the real layout."""
    return f"【占位】\n{description}\n"


def main(argv: list[str] | None = None) -> int:
    return common.run(
        argv, program="skill_zh.py",
        description="Translate one skill's SKILL.md body into Chinese.",
        angle=common.SKILL_ZH_ANGLE, build_request=_request, produce=_produce,
        placeholder=placeholder)


if __name__ == "__main__":
    raise SystemExit(main())
