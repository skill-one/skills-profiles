#!/usr/bin/env python3
"""Translate one skill's SKILL.md body into Simplified Chinese, over the same chat API.

The third angle on a skill, beside domain.json and description_zh.json: the body of the skill's
own page in, its Chinese translation out. Only the translation is written - the page is not an
installation, and the identifying metadata (name, description) already lives in the catalog and
the other two angle files.

    skill_zh.py <skill> [--print]   translate one skill, or print the first request, calling nothing

A body too long for one answer travels in pieces: the body is cut on its own markdown seams -
never inside a code fence that fits in one piece - each piece is translated in its own call, and
the page is written only when every piece came back. A file is whole or absent, as ever.

The turns are rendered from `prompts/skill_zh.md` and `prompts/skill_zh_user.md`; the endpoint,
the layout, the gate and the contract are the ones `translate.py` and `common.py` already hold.

Driven by the justfile, one process per skill.
"""

import re

import common
import translate
from common import Config

# The two prompts, beside the other angles': the system task and the one user turn.
PROMPT = "skill_zh.md"
USER_PROMPT = "skill_zh_user.md"
# The one target language the templates are rendered with; the value is the language as it is
# named in the prompt itself.
TO = "Simplified Chinese (简体中文)"
# The seam lines a body is cut between: a code fence opens or closes here, and a cut never
# lands between the two while the block itself fits in one piece.
FENCE = re.compile(r"^\s*(?:```|~~~)")
# One piece's own budget: a Chinese rendering of this many characters, thinking included, stays
# inside the answer budget the channel allows (16384 tokens on the GLM one). A piece is what one
# call translates whole; the page is the pieces, rejoined on the seams they were cut on.
MAX_CHUNK_CHARS = 16000


def blocks(text: str) -> list[str]:
    """The body's fence-aware blocks: a blank line outside a fence is the page's paragraph seam,
    and a code fence holds its lines together whatever blank lines it carries.

    The seam itself travels with neither block - the assembler puts it back.
    """
    out: list[str] = []
    block: list[str] = []
    fenced = False
    for line in text.splitlines(keepends=True):
        if FENCE.match(line):
            fenced = not fenced
        if not fenced and not line.strip():
            if block:
                out.append("".join(block).rstrip("\n"))
                block = []
            continue
        block.append(line)
    if block:
        out.append("".join(block).rstrip("\n"))
    return out


def cut_lines(block: str, size: int) -> list[str]:
    """One block too big for a piece of its own - a wall of prose, a long fence - cut between
    lines as the last resort. Each part is under `size` unless a single line is longer than the
    whole budget; that line rides whole and lets the truncation guard speak."""
    parts: list[str] = []
    part = ""
    for line in block.splitlines(keepends=True):
        if part and len(part) + len(line) > size:
            parts.append(part.rstrip("\n"))
            part = ""
        part += line
    if part:
        parts.append(part.rstrip("\n"))
    return parts


def chunks(text: str, size: int = MAX_CHUNK_CHARS) -> list[str]:
    """The body in pieces one call can translate whole: whole blocks packed up to `size`, every
    piece meeting the next on the paragraph seam the assembler will put back."""
    pieces: list[str] = []
    piece = ""
    for block in blocks(text):
        for part in [block] if len(block) <= size else cut_lines(block, size):
            if piece and len(piece) + len(part) > size:
                pieces.append(piece)
                piece = ""
            piece = f"{piece}\n\n{part}" if piece else part
    if piece:
        pieces.append(piece)
    return pieces


def messages(config: Config, text: str) -> list[dict]:
    """The one chat turn for one piece: the task rendered for the target language, then the
    piece to render into it - and nothing else.

    The piece goes in as a template variable rather than text of the template, so braces in a
    skill's own words can never be read as Jinja.
    """
    system = common.render(common.load_prompt(config, PROMPT), to=TO)
    user = common.render(common.load_prompt(config, USER_PROMPT), to=TO, text=text)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def chunk_bodies(config: Config, body_text: str) -> list[dict]:
    """One chat body per piece: the same deterministic, non-streaming request shape the
    description angle sends, one per piece of the page."""
    return [translate.chat_body(config, messages(config, piece)) for piece in chunks(body_text)]


def _request(config: Config, skill: str, source: str, _description: str) -> dict:
    """The chat body for the body's first piece - every piece's request is the same shape - and
    the one gate the angle adds: a body with nothing in it is dropped before any call."""
    body_text = common.skill_body(source)
    if not body_text.strip():
        raise SystemExit(f"{skill}: body is empty - not translated")
    return chunk_bodies(config, body_text)[0]


def _produce(config: Config, _body: dict, source: str) -> str:
    """The one Chinese page: every piece translated in turn over the shared endpoint and its
    fallback, rejoined on the paragraph seams. One failed piece fails the page - a half
    translation is never written."""
    translator = translate.Translator(config)
    pieces = [translator.ask(body) for body in chunk_bodies(config, common.skill_body(source))]
    return "\n\n".join(pieces).strip() + "\n"


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
