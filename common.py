#!/usr/bin/env python3
"""The kernel both producers share: settings, the tree, the source, prompts, writes, calls, CLI.

`jev.py` and `translate.py` are two thin angles over everything here - one typed endpoint and one
chat endpoint - and `index.py`, `stale.py` and `readme.py` read the same tree through it.
"""

import argparse
import json
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

# The output root holds three layers, and they do not overlap: the source pages the angles read
# (one SKILL.md per skill), the profiles this project writes about them, and the mirror's own
# files the tree reads (its index above all) that the sources were taken from.
SKILLS_DIR = "skills"
PROFILES_DIR = "profiles"
UPSTREAM_DIR = "upstream"
SKILL_MD = "SKILL.md"
INDEX = "skills.jsonl"

# The three angles, each one file in a skill's profile directory and one field in the catalog.
DOMAIN_ANGLE = "domain"
TRANSLATE_ANGLE = "description_zh"
SKILL_ZH_ANGLE = "skill_zh"  # the one text angle: its file is skill_zh.md, not skill_zh.json

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

# 302.AI serves System One under the provider's own namespace; its generic `/v1` gateway has no
# channel for one and answers `503 no available models` whatever model is asked for.
DOMAIN_BASE_URL = "https://api.302.ai/typesafeai/v1/systemone"
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
    # the endpoints answer in one to three seconds, and a dropped request never answers at all, so
    # the timeout is what decides how long a dead call waits before the retry that rescues it. With
    # thinking on, a translation call is slower than that - raise SKILLS_PROFILES_TIMEOUT locally.
    timeout: float = 20.0
    max_retries: int = 3
    dry_run: bool = False

    prompts_dir: Path = Path("prompts")
    output_dir: Path = Path("output")


# --------------------------------------------------------------------------- the tree


def skill_dir_name(skill: str) -> str:
    """The `_` spelling upstream writes for `:` and `&` in an id."""
    return skill.replace(":", "_").replace("&", "_")


def skill_md_path(config: Config, skill: str) -> Path:
    """The skill's own SKILL.md as the mirror published it, beside the profile written from it."""
    return config.output_dir / SKILLS_DIR / skill_dir_name(skill) / SKILL_MD


def profile_dir(config: Config, skill: str) -> Path:
    return config.output_dir / PROFILES_DIR / skill_dir_name(skill)


def profile_path(config: Config, skill: str, angle: str) -> Path:
    """profiles/<skill>/<angle>.json: where one producer writes its one file."""
    return profile_dir(config, skill) / f"{angle}.json"


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


def skill_source(config: Config, skill: str) -> str:
    """The skill's own text at the state's budget: what a state-building angle reads."""
    return cap_source(skill_md(config, skill))


def skill_body(source: str) -> str:
    """The source without its front matter: the name and the description lead the state already."""
    return FRONT_MATTER.sub("", source, count=1).lstrip("\n")


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


# ----------------------------------------------------------------------------- the HTTP call


def worth_retrying(error: httpx.HTTPError) -> bool:
    """A dropped connection or a busy gateway is worth the next try; a rejected body is not."""
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in {429, 500, 502, 503, 504}
    return True  # a timeout or a transport error never reached an answer


def post_json(client: httpx.Client, url: str, key: str, body: dict, max_retries: int) -> Any:
    """POST one Bearer-authenticated json body and parse the answer, with the shared retry reading.

    The first call after an endpoint has been idle is regularly dropped with no response at all,
    which arrives as a timeout, so a dropped call is retried rather than recorded as a skill that
    could not be built. A rejected body (400) fails at once.
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
            time.sleep(2 ** attempt)


# --------------------------------------------------------- the one command both producers are


def run(argv: list[str] | None, *, program: str, description: str, angle: str,
        build_request: Callable[[Config, str, str, str], dict],
        produce: Callable[[Config, dict, str], Any],
        placeholder: Callable[[str], Any]) -> int:
    """The whole command the producers share: one skill in, one angle file written.

    `build_request(config, skill, source, description)` shapes the call; `produce(config, body,
    source)` makes it and shapes the answer, raising on a bad one; `placeholder(description)` is
    the dry run. A dict answer is written as `<angle>.json`, a str answer as `<angle>.md`.
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

    body = build_request(config, args.skill, source, line)
    if args.print_request:
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return 0

    if config.dry_run:
        output = placeholder(line)
    else:
        try:
            output = produce(config, body, source)
        except (httpx.HTTPError, RuntimeError) as error:
            print(f"{args.skill}: {type(error).__name__}: {error}", file=sys.stderr)
            return 1
    path = profile_path(config, args.skill, angle)
    if isinstance(output, str):  # the text angle: one markdown page, not one json object
        written = write_atomic(path.with_suffix(".md"), output)
    else:
        written = write_json(path, output)
    print(f"built {written}", file=sys.stderr)
    return 0
