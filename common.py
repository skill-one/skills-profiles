#!/usr/bin/env python3
"""The kernel both producers share: settings, the tree, the source, prompts, writes, calls, CLI.

`jev.py` and `skill_zh.py` are two thin angles over everything here - one typed endpoint and one
chat endpoint - and `index.py` and `readme.py` read the same tree through it.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import yaml
from jinja2 import Environment, StrictUndefined
from pydantic_settings import BaseSettings, SettingsConfigDict

# The output root holds one layer per skill plus the catalog: `skills/<id>/` holds the source
# page and, beside it, what this project wrote about it - the catalog `skills.jsonl` joins them.
# The mirror's listing is pulled fresh by `just sync` into the catalog, which is its only
# lasting trace.
SKILLS_DIR = "skills"
SKILL_MD = "SKILL.md"
INDEX = "skills.jsonl"

# The two angles, each one file in a skill's directory and its fields in the catalog. The file
# names spell the generated one as a sibling of the source page: a `.` and the locale, so the
# directory installs as a skill with its annotation riding along. The Chinese description is not
# a file of its own - it is the `description` in the zh page's front matter, assembled here.
DOMAIN_ANGLE = "domain"
SKILL_ZH_ANGLE = "skill_zh"
ANGLE_FILES = {DOMAIN_ANGLE: "domain.json", SKILL_ZH_ANGLE: "SKILL.zh.md"}

MAX_SKILL_MD_CHARS = 20000
# A repository can be one skill or several hundred (`awesome-*` collections). The cap keeps the
# context a few thousand characters whatever the repo is, and what was left out is counted.
MAX_SIBLINGS = 50
# A sibling's own description is sometimes a page rather than a line. Each is cut to a hint, and
# the slugs beside them carry the rest.
MAX_SIBLING_CHARS = 300
# libyaml where there is one, which every PyYAML wheel carries, and the pure-Python loader where a
# source build left it out.
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
# The header is where a skill's name and description are written down; what sits beside them -
# `license`, `allowed-tools`, a version - is about installing a skill rather than what it is for.
FRONT_MATTER = re.compile(r"\A\s*---\r?\n(.*?)\r?\n---\r?\n", re.S)
# A source that just stops reads as one that ended, and an answer can then be confidently wrong
# about the part that was never sent. Said in the prompt's language, and inside the source.
TRUNCATION_NOTE = "[注: 这份正文过长, 以上仅为开头, 余下内容已省略]"

# TypeSafe's own API for its System One protocol. 302.AI proxies the same path, but its channel
# answers 402 once the TypeSafe credits behind it run out - the official endpoint is the baseline.
DOMAIN_BASE_URL = "https://api.typesafe.ai/v1/systemone"
DOMAIN_MODEL = "jev-latest"
# Xunfei Xingchen MaaS, OpenAI protocol (the address for services published after 2026-01-10).
TRANSLATE_BASE_URL = "https://maas-api.cn-huabei-1.xf-yun.com/v2"
# The model id the MaaS console's service page shows for Spark-X2.5-4B; override when it differs.
TRANSLATE_MODEL = "spark-x2.5-4b"
# Agnes AI, OpenAI protocol: the second chat endpoint a skill the first one fails is retried on.
TRANSLATE_FALLBACK_BASE_URL = "https://apihub.agnes-ai.com/v1"
TRANSLATE_FALLBACK_MODEL = "agnes-3.0-flash"

_env = Environment(autoescape=False, keep_trailing_newline=True, undefined=StrictUndefined)


class Config(BaseSettings):
    """Settings under the `SKILLS_PROFILES_` prefix: `.env` holds the two endpoints and their keys."""

    model_config = SettingsConfigDict(
        env_prefix="SKILLS_PROFILES_", env_file=".env", env_file_encoding="utf-8",
        extra="ignore", env_ignore_empty=True)

    # the typed System One endpoint
    api_key: str | None = None
    base_url: str = DOMAIN_BASE_URL
    # an alias rather than a version: pin `jev-1.13.0` to keep a threshold meaning the same thing
    model: str = DOMAIN_MODEL
    # the OpenAI-compatible chat endpoint translate.py asks
    translate_api_key: str | None = None
    translate_base_url: str = TRANSLATE_BASE_URL
    translate_model: str = TRANSLATE_MODEL
    # the second chat endpoint translate.py hands a failed skill to, once. It shares TIMEOUT,
    # MAX_RETRIES and the token budget with the primary; its key is said separately, not borrowed
    # from `api_key`, so the two endpoints can change apart.
    translate_fallback_api_key: str | None = None
    translate_fallback_base_url: str = TRANSLATE_FALLBACK_BASE_URL
    translate_fallback_model: str = TRANSLATE_FALLBACK_MODEL
    # Deep thinking: the endpoint reasons into `reasoning_content` before answering. It is not read
    # - the translation still arrives in `content` - but the model thinks first. On by default.
    translate_enable_thinking: bool = True
    # The answer's whole token budget, reasoning included. The endpoint's own default (2048) would
    # cut the thinking off mid-sentence; the documented ceiling is 32768, which is the "think as
    # long as it takes" setting for a one-line translation.
    translate_max_tokens: int = 32768
    # The chat endpoint's own seconds per request. A thinking call reasons before it answers and
    # routinely runs past the typed endpoint's patience, so this has its own, slower default.
    translate_timeout: float = 120.0
    # the typed endpoint answers in one to three seconds, and a dropped request never answers at
    # all, so the timeout is what decides how long a dead call waits before the retry that rescues
    # it. The chat endpoint does not share it - see translate_timeout above.
    timeout: float = 20.0
    max_retries: int = 3
    dry_run: bool = False

    prompts_dir: Path = Path("prompts")
    output_dir: Path = Path("output")


# --------------------------------------------------------------------------- the tree


def skill_dir_name(skill: str) -> str:
    """The `_` spelling upstream writes for `:` and `&` in an id."""
    return skill.replace(":", "_").replace("&", "_")


def skill_dir(config: Config, skill: str) -> Path:
    """The skill's one directory: its source page and its angles' files together."""
    return config.output_dir / SKILLS_DIR / skill_dir_name(skill)


def skill_md_path(config: Config, skill: str) -> Path:
    """The skill's own SKILL.md as fetched from its repository, beside what this project wrote."""
    return skill_dir(config, skill) / SKILL_MD


def angle_path(config: Config, skill: str, angle: str) -> Path:
    """One angle's file, beside the source page it was built from: the generated sibling."""
    return skill_dir(config, skill) / ANGLE_FILES[angle]


# ----------------------------------------------------------------------- the skill source


def skill_md(config: Config, skill: str) -> str:
    """The skill's own SKILL.md, whole: the text as the mirror published it."""
    return skill_md_path(config, skill).read_text(encoding="utf-8", errors="replace")


def cap_source(text: str) -> str:
    """The state's budget over a source: past MAX_SKILL_MD_CHARS it is cut on a line break and
    the cut is announced."""
    if len(text) <= MAX_SKILL_MD_CHARS:
        return text
    cut = text.rfind("\n", 0, MAX_SKILL_MD_CHARS)
    head = text[:cut] if cut > 0 else text[:MAX_SKILL_MD_CHARS]
    return f"{head.rstrip()}\n\n{TRUNCATION_NOTE}\n"


def skill_body(source: str) -> str:
    """The source without its front matter: the name and the description lead the state already."""
    return FRONT_MATTER.sub("", source, count=1).lstrip("\n")


def front_matter(fields: dict) -> str:
    """Valid YAML from the fields given: the header a generated page carries, assembled here so
    the model never shapes it - a broken header is a description no one can read back."""
    block = yaml.dump(fields, allow_unicode=True, sort_keys=False, default_flow_style=False,
                      width=1000000)
    return f"---\n{block}---\n"


def skill_description(source: str) -> str:
    """The skill's own one-line description: its front matter's `description`, as YAML.

    Empty means nothing to lead with rather than a description that happens to be short, and the
    command drops the skill on it.
    """
    block = FRONT_MATTER.match(source)
    if block is None:
        return ""
    try:
        front = yaml.load(block.group(1), Loader=YAML_LOADER)
    except yaml.YAMLError:
        return ""
    description = front.get("description") if isinstance(front, dict) else None
    return description.strip() if isinstance(description, str) else ""


def skill_name(source: str) -> str:
    """The skill's own front matter `name`, or nothing when there is none. The mirror spells a
    skill's slug out of this field, the tree out of the directory the source sat in."""
    block = FRONT_MATTER.match(source)
    if block is None:
        return ""
    try:
        front = yaml.load(block.group(1), Loader=YAML_LOADER)
    except yaml.YAMLError:
        return ""
    name = front.get("name") if isinstance(front, dict) else None
    return name.strip() if isinstance(name, str) else ""


def repository(config: Config, skill: str) -> dict | None:
    """The context a skill's own repository gives: its id, and the siblings beside it.

    A sibling contributes its own one-line description and nothing else: its body would be a
    second skill's body. A repository with no sibling says nothing the skill's own name has not
    already said, so it is not sent at all rather than sent empty.
    """
    parts = skill_dir_name(skill).split("/")
    if len(parts) != 3:
        return None
    owner, repo, own = parts
    root = config.output_dir / SKILLS_DIR / owner / repo
    if not root.is_dir():
        return None
    siblings = []
    for child in sorted(root.iterdir()):
        source = child / SKILL_MD
        if child.name == own or not source.is_file():
            continue
        one_line = " ".join(skill_description(
            source.read_text(encoding="utf-8", errors="replace")).split())
        if len(one_line) > MAX_SIBLING_CHARS:
            one_line = one_line[:MAX_SIBLING_CHARS].rsplit(" ", 1)[0].rstrip() + "…"
        siblings.append(f"{child.name}: {one_line}" if one_line else child.name)
    if not siblings:
        return None
    return {"id": f"{owner}/{repo}", "siblings": siblings[:MAX_SIBLINGS],
            "more": max(0, len(siblings) - MAX_SIBLINGS)}


# ------------------------------------------------------------------------ prompts and writes


def load_prompt(config: Config, name: str) -> str:
    """One prompt file under prompts_dir, stripped: the only place prose for a call lives."""
    return (config.prompts_dir / name).read_text(encoding="utf-8").strip()


def render(template: str, **context: Any) -> str:
    """Render one Jinja template with strict undefineds: a missing variable fails loudly."""
    return _env.from_string(template).render(**context)


def write_atomic(path: Path, text: str) -> Path:
    """Write a text file renamed into place: a half-written one would read as done to the batch."""
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    partial.write_text(text, encoding="utf-8")
    partial.replace(path)
    return path


def write_json(path: Path, payload: dict) -> Path:
    """One json object, atomic, unescaped Chinese."""
    return write_atomic(path, json.dumps(payload, ensure_ascii=False))


def read_jsonl(path: Path) -> list[dict]:
    """The rows of one jsonl file, in its own order. A line that is not valid json is an error
    naming the file and the line, never a silently shorter catalog."""
    rows: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as error:
            raise ValueError(f"{path}: line {line_no} is not valid JSON") from error
        if isinstance(row, dict):
            rows.append(row)
    return rows


# ----------------------------------------------------------------------------- the HTTP call


def worth_retrying(error: httpx.HTTPError) -> bool:
    """A dropped connection or a busy gateway is worth the next try; a rejected body is not."""
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in {429, 500, 502, 503, 504}
    return True  # a timeout or a transport error never reached an answer


def backoff(attempt: int) -> None:
    """Exponential backoff with jitter: a pool of callers a gateway just throttled must not all
    knock again at the same moment."""
    time.sleep(2 ** attempt + random.random())


def post_json(client: httpx.Client, url: str, key: str, body: dict, max_retries: int) -> Any:
    """POST one Bearer-authenticated json body and parse the answer, with the shared retry reading.

    The first call after an endpoint has been idle is regularly dropped with no response at all,
    which arrives as a timeout, so a dropped call is retried rather than recorded as a skill that
    could not be built. A rejected body (400) - and a 200 that is not json - fail at once: the
    chat caller still has its fallback endpoint for those.
    """
    attempt = 0
    while True:
        try:
            response = client.post(url, headers={"Authorization": f"Bearer {key}"}, json=body)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError as error:
                raise RuntimeError("response was not valid JSON") from error
        except httpx.HTTPError as error:
            if attempt >= max_retries or not worth_retrying(error):
                raise
            attempt += 1
            backoff(attempt)


# --------------------------------------------------------- the one command both producers are


class UnusableInput(Exception):
    """A skill that cannot be built: a gate `run()` reports as one stderr line and exit 1."""


def run(argv: list[str] | None, *, program: str, description: str, angle: str,
        build_requests: Callable[[Config, str, str], list[dict]],
        produce: Callable[[Config, list[dict], str], Any],
        placeholder: Callable[[str], Any]) -> int:
    """The whole command the producers share: one skill in, one angle file written.

    `build_requests(config, skill, source)` shapes every call the angle makes, computed once;
    `produce(config, requests, source)` makes them and shapes the answer, raising on a bad one;
    `placeholder(description)` is the dry run. A dict answer is written as `<angle>.json`, a str
    answer as `<angle>.md`.
    Exit: 0 built, 1 unusable input or endpoint, 2 bad arguments.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("skill", nargs="?",
                        help="skill directory in the snapshot: owner/repo/slug")
    parser.add_argument("--print", dest="print_request", action="store_true",
                        help="print the request and stop, calling nothing")
    args = parser.parse_args(argv)

    if args.skill is None:
        print(f"usage: {program} <skill>   (owner/repo/slug in the snapshot)", file=sys.stderr)
        return 2

    config = Config()
    try:
        source = skill_md(config, args.skill)
    except FileNotFoundError as error:
        print(f"{error.filename}: not found", file=sys.stderr)
        return 1
    # the gate on a skill, for both angles: both are built from the line saying what it is for, so
    # a skill whose own header yields none is dropped here rather than guessed at
    line = skill_description(source)
    if not line:
        print(f"{args.skill}: no description in its front matter", file=sys.stderr)
        return 1

    try:
        requests = build_requests(config, args.skill, source)
    except UnusableInput as error:
        print(f"{args.skill}: {error}", file=sys.stderr)
        return 1
    if args.print_request:
        # one request prints as the object; an angle that makes several prints them as an array
        shown: object = requests[0] if len(requests) == 1 else requests
        print(json.dumps(shown, ensure_ascii=False, indent=2))
        return 0

    if config.dry_run:
        output = placeholder(line)
    else:
        try:
            output = produce(config, requests, source)
        except (httpx.HTTPError, RuntimeError, UnusableInput) as error:
            print(f"{args.skill}: {type(error).__name__}: {error}", file=sys.stderr)
            return 1
    path = angle_path(config, args.skill, angle)
    # the text angle writes one markdown page; the others one json object
    written = write_atomic(path, output) if isinstance(output, str) else write_json(path, output)
    print(f"built {written}", file=sys.stderr)
    return 0
