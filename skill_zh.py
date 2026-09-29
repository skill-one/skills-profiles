#!/usr/bin/env python3
"""Build one skill's Chinese page, SKILL.zh.md, over the same chat API.

The second angle on a skill, beside domain.json. One process makes every call the page needs:
the description is translated first, then the body, and the page - the front matter with the
Chinese description in it, over the translated body - is assembled by code and written only when
every call came back. The model never shapes the front matter: YAML is the one strictly parsed
part of the page, so it is never left to a model's hands.

    skill_zh.py <skill> [--print]   build one page, or print the first request, calling nothing

A body too long for one answer travels in pieces: the body is cut on its own markdown seams -
never inside a code fence that fits in one piece - each piece is translated in its own call
carrying the seam it was cut on, and the page is written only when every piece came back. A file
is whole or absent, as ever.

The turns are rendered from `prompts/translate.md`, `prompts/translate_user.md`,
`prompts/skill_zh.md` and `prompts/skill_zh_user.md`; the endpoint, the layout, the gate and the
contract are the ones `translate.py` and `common.py` already hold.

Driven by `batch.py`, one skill per pool job.
"""

from __future__ import annotations

import re

import yaml

import common
import translate
from common import Config

# The two prompts, beside the other angles': the system task and the one user turn.
PROMPT = "skill_zh.md"
USER_PROMPT = "skill_zh_user.md"
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


def chunks(text: str, size: int = MAX_CHUNK_CHARS) -> list[tuple[str, str]]:
    """The body in pieces one call can translate whole, each carrying the seam that preceded it:
    whole blocks packed up to `size`; a block cut between lines sends its next part with the
    line seam it was cut on, so the rejoined page is the body again - a cut table stays a table."""
    pieces: list[tuple[str, str]] = []
    piece = ""
    seam = ""
    for block in blocks(text):
        parts = [block] if len(block) <= size else cut_lines(block, size)
        for i, part in enumerate(parts):
            joiner = "\n" if i else "\n\n"  # a block meets the page on its paragraph seam
            if not piece:
                seam = joiner if pieces else ""
            elif len(piece) + len(part) > size:
                pieces.append((piece, seam))
                piece, seam = "", joiner
            piece = f"{piece}{joiner}{part}" if piece else part
    if piece:
        pieces.append((piece, seam))
    return pieces


def rejoin(pieces: list[tuple[str, str]]) -> str:
    """The page body: the pieces back on the seams they travelled with."""
    return "".join(f"{seam}{text}" for text, seam in pieces).strip()


def chunk_bodies(config: Config, body_text: str) -> list[dict]:
    """One chat body per piece: the same deterministic, non-streaming request shape the
    description angle sends, one per piece of the page."""
    return [translate.chat_body(config, translate.turns(config, piece, PROMPT, USER_PROMPT))
            for piece, _ in chunks(body_text)]


def _requests(config: Config, skill: str, source: str) -> list[dict]:
    """Every chat body the page needs, shaped once: the description call first, then one call per
    body piece. The one gate the angle adds: a body with nothing in it is dropped before any call."""
    body_text = common.skill_body(source)
    if not body_text.strip():
        raise common.UnusableInput("body is empty - not translated")
    return [translate.request_body(config, common.skill_description(source)),
            *chunk_bodies(config, body_text)]


def _page(source: str, zh_description: str, pieces: list[tuple[str, str]]) -> str:
    """The one Chinese page: the front matter assembled by code over the rejoined body. One failed
    call fails the page before this runs - a half translation is never written."""
    body = rejoin(pieces)
    fields: dict = {}
    block = common.FRONT_MATTER.match(source)
    if block is not None:
        loaded = yaml.load(block.group(1), Loader=common.YAML_LOADER)
        if isinstance(loaded, dict) and isinstance(loaded.get("name"), str):
            fields["name"] = loaded["name"]
    fields["description"] = zh_description
    return f"{common.front_matter(fields)}\n{body}\n"


def _produce(config: Config, bodies: list[dict], source: str) -> str:
    """The description is the first request; its answer leads the front matter, and the body
    pieces' answers are rejoined on the seams their requests were cut on, all over the shared
    endpoint and its fallback."""
    translator = translate.Translator(config)
    zh_description = translator.ask(bodies[0])
    pieces = [(translator.ask(body), seam)
              for (body, (_, seam)) in zip(bodies[1:], chunks(common.skill_body(source)),
                                           strict=True)]
    return _page(source, zh_description, pieces)


def placeholder(description: str) -> str:
    """A value shaped like the answer, so `just dry=1 skill-zh` still writes the real layout."""
    return f"{common.front_matter({'description': f'【占位】{description}'})}\n【占位】\n{description}\n"


def main(argv: list[str] | None = None) -> int:
    return common.run(
        argv, program="skill_zh.py",
        description="Translate one skill's SKILL.md body into Chinese.",
        angle=common.SKILL_ZH_ANGLE, build_requests=_requests, produce=_produce,
        placeholder=placeholder)


if __name__ == "__main__":
    raise SystemExit(main())
