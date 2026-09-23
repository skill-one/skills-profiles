#!/usr/bin/env python3
"""Label one skill's `domain` with Jev (TypeSafe System One) over 302.AI.

Its endpoint is not OpenAI-compatible - a `state` and typed `questions` in, typed `answers` out,
and no free text. The state is rendered from `prompts/_system.md`: the skill's name, the
description out of its own front matter, its `SKILL.md` body, and - the one extra layer `domain`
gets - the sibling skills beside it in its repository, a category being a property of the
repository rather than of one file.

    jev.py <skill> [--print]   label one skill, or print the request and call nothing

Driven by the justfile, one process per skill.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import httpx
import yaml
from jinja2 import Environment, StrictUndefined
from pydantic_settings import BaseSettings, SettingsConfigDict

_env = Environment(autoescape=False, keep_trailing_newline=True, undefined=StrictUndefined)
# The output root holds three layers, and they do not overlap: the skill directories the mirror
# publishes and a user installs, the labels this project writes about them, and the rest of the
# mirror (its index, repositories, avatars) that the sources were taken from.
SKILLS_DIR = "skills"
PROFILES_DIR = "profiles"
UPSTREAM_DIR = "upstream"
SKILL_MD = "SKILL.md"
SYSTEM_MD = "_system.md"
INDEX = "skills.jsonl"
ANGLE = "domain"
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
BASE_URL = "https://api.302.ai/typesafeai/v1/systemone"

# The taxonomy, stated once. Jev is handed the categories and their own words as the `criteria` its
# answer is confined to, so there is no second copy of the list to keep in step and no decoder to
# enforce - which is the whole of what a typed answer buys over a chat model's json.
CRITERIA = {
    "development": "planning, designing and writing software: code, debugging, refactoring, git & "
                   "version control, databases, API/framework integration, web scraping & browser "
                   "automation, developer workflows (CI, builds, dependencies), and tooling for "
                   "any of those",
    "testing": "writing tests & test frameworks, E2E/UI test automation, code review, quality "
               "checks & bug hunting",
    "data-analysis": "SQL, data cleaning, statistics, visualization, reporting & data engineering "
                     "(ETL)",
    "devops-security": "deployment & release, cloud infrastructure, monitoring & alerting, SRE, "
                       "networking & security",
    "office-productivity": "docx/pdf/xlsx/ppt document processing, email, calendar, meeting notes, "
                           "and personal or team coordination (todos, schedules, follow-ups). "
                           "Software project management (git, issues, CI) does NOT belong here",
    "content-creation": "articles, copywriting, translation, technical docs, social media content, "
                        "podcasts/scripts - creation centered on text and information",
    "design-media": "UI/graphic design, image generation & editing, video editing, 3D, brand "
                    "visuals",
    "knowledge-management": "notes & knowledge bases (Obsidian/Notion etc.), information "
                            "retrieval, deep research, organizing material",
    "business-ops": "marketing, SEO, sales, customer service, e-commerce, growth & CRM - work "
                    "aimed at business growth and customers",
    "finance-payment": "payment integration, billing & invoices, investing, trading",
    "education": "teaching and learning: lesson prep, course creation, tutoring, homework, "
                 "explaining a subject to someone who is learning it",
    "lifestyle": "travel planning, food, fitness & health, personal errands",
    "other": "only when nothing above fits at all: if a category describes what the skill is for, "
             "name that one rather than falling back here",
}
# The task, and the one rule the taxonomy leans on: a skill is what it is for, not how it works.
INSTRUCTION = (
    "Which single category does this skill primarily belong to?\n"
    "1. Judge what the skill is for, not how it works or what it is written in: the interface it "
    "uses - a script, a CLI, an API wrapper - is not its category, and a tool that draws, watches "
    "or writes belongs to the category of what it produces.\n"
    "2. When several categories fit, choose the one the skill's main output serves.")
# The one question of the one call: a closed choice over the taxonomy above.
QUESTION = {"domain": {"type": "choice", "instructions": INSTRUCTION, "criteria": CRITERIA}}


class Config(BaseSettings):
    """Settings under the `SKILLS_PROFILES_` prefix: `.env` holds the endpoint and its key."""

    model_config = SettingsConfigDict(
        env_prefix="SKILLS_PROFILES_", env_file=".env", env_file_encoding="utf-8",
        extra="ignore", env_ignore_empty=True)

    api_key: str | None = None
    base_url: str = BASE_URL
    # an alias rather than a version: pin `jev-1.13.0` to keep a threshold meaning the same thing
    model: str = "jev-latest"
    # the endpoint answers in one to three seconds, and a dropped request never answers at all, so
    # the timeout is what decides how long a dead call waits before the retry that rescues it
    timeout: float = 20.0
    max_retries: int = 3
    dry_run: bool = False

    prompts_dir: Path = Path("prompts")
    output_dir: Path = Path("output")


def skill_dir_name(skill: str) -> str:
    """The `_` spelling upstream writes for `:` and `&` in an id."""
    return skill.replace(":", "_").replace("&", "_")


def profile_dir(config: Config, skill: str) -> Path:
    return config.output_dir / PROFILES_DIR / skill_dir_name(skill)


def json_path(config: Config, skill: str) -> Path:
    return profile_dir(config, skill) / f"{ANGLE}.json"


def skill_source_path(config: Config, skill: str) -> Path:
    """The skill's own directory as the mirror published it, beside the label written from it."""
    return config.output_dir / SKILLS_DIR / skill_dir_name(skill) / SKILL_MD


def skill_source(config: Config, skill: str) -> str:
    """The skill's own text, capped at MAX_SKILL_MD_CHARS, cut on a line break and announced."""
    text = skill_source_path(config, skill).read_text(encoding="utf-8", errors="replace")
    if len(text) <= MAX_SKILL_MD_CHARS:
        return text
    cut = text.rfind("\n", 0, MAX_SKILL_MD_CHARS)
    head = text[:cut] if cut > 0 else text[:MAX_SKILL_MD_CHARS]
    return f"{head.rstrip()}\n\n{TRUNCATION_NOTE}\n"


def skill_body(source: str) -> str:
    """The source without its front matter: the name and the description lead the state already."""
    return FRONT_MATTER.sub("", source, count=1).lstrip("\n")


def skill_description(source: str) -> str:
    """The skill's own one-line description: its front matter's `description`, as YAML.

    Empty means nothing to lead with rather than a description that happens to be short, and
    `main` drops the skill on it.
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


def render(template: str, body: str, description: str, name: str,
           repo: dict | None = None) -> str:
    return _env.from_string(template).render(
        skill_body=body, description=description, name=name, repo=repo)


def state(config: Config, skill: str, source: str) -> str:
    """The system message, plus the repository: the one layer that disambiguates a lone skill."""
    template = (config.prompts_dir / SYSTEM_MD).read_text(encoding="utf-8").strip()
    return render(template, skill_body(source), skill_description(source), skill,
                  repository(config, skill))


def request_body(model: str, state_text: str) -> dict:
    """The one body this endpoint takes: a state, the question about it, and no messages."""
    return {"model": model, "state": state_text, "questions": QUESTION}


def worth_retrying(error: httpx.HTTPError) -> bool:
    """A dropped connection or a busy gateway is worth the next try; a rejected body is not."""
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in {429, 500, 502, 503, 504}
    return True  # a timeout or a transport error never reached an answer


class Jev:
    """One `POST /v1/systemone`: a state, a typed question, a typed answer, and no text."""

    def __init__(self, config: Config, client: httpx.Client | None = None):
        if not config.api_key:
            raise SystemExit("SKILLS_PROFILES_API_KEY is not set - nothing to call with")
        self.config = config
        self.client = client or httpx.Client(timeout=config.timeout)

    def ask(self, body: dict) -> dict:
        """The question against the state, in one call: the answer back.

        The first call after the endpoint has been idle is regularly dropped with no response at
        all, which arrives as a timeout, so a dropped call is retried rather than recorded as a
        skill that could not be built.
        """
        attempt = 0
        while True:
            try:
                response = self.client.post(
                    self.config.base_url,
                    headers={"Authorization": f"Bearer {self.config.api_key}"}, json=body)
                response.raise_for_status()
                return response.json().get("answers", {})
            except httpx.HTTPError as error:
                if attempt >= self.config.max_retries or not worth_retrying(error):
                    raise
                attempt += 1
                time.sleep(2 ** attempt)


def choice(answer: object) -> str | None:
    """The option the endpoint picked, as its answer spells it."""
    picked = answer.get("choice") if isinstance(answer, dict) else answer
    return picked if isinstance(picked, str) else None


def confidence(answer: object) -> float | None:
    """How sure the endpoint says it is, derived from the distribution rather than guessed."""
    value = answer.get("confidence") if isinstance(answer, dict) else None
    return float(value) if isinstance(value, (int, float)) else None


def probabilities(answer: object) -> dict:
    """The distribution the choice was read off: every option of the enum, and the mass it holds."""
    value = answer.get("probabilities") if isinstance(answer, dict) else None
    return dict(value) if isinstance(value, dict) else {}


def profile(answers: dict) -> dict:
    """Jev's answer as the profile's json: the category it chose, how sure it was, and the rest.

    The guard on the way in is the decoder this path does not have: the request used to enforce
    the enum, so an answer outside it is checked.
    """
    answer = answers.get(ANGLE)
    picked = choice(answer)
    if picked not in CRITERIA:
        raise RuntimeError(f"chose {picked!r}, which is not a category")
    return {"domain": picked, "confidence": confidence(answer),
            "probabilities": probabilities(answer)}


def placeholder() -> dict:
    """A value shaped like the answer, so `just dry=1` still writes the real layout."""
    first = next(iter(CRITERIA))
    return {"domain": first, "confidence": 1.0,
            "probabilities": {name: 1.0 if name == first else 0.0 for name in CRITERIA}}


def write(config: Config, skill: str, output: dict) -> Path:
    """Write domain.json, renamed into place: a half-written one would read as done to the batch."""
    path = json_path(config, skill)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    partial.write_text(json.dumps(output, ensure_ascii=False), encoding="utf-8")
    partial.replace(path)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Label one skill's domain.")
    parser.add_argument("skill", nargs="?", help="skill directory in the snapshot: owner/repo/slug")
    parser.add_argument("--print", dest="print_request", action="store_true",
                        help="print the request and stop, calling nothing")
    args = parser.parse_args(argv)

    if args.skill is None:
        print("usage: jev.py <skill>   (owner/repo/slug in the snapshot)", file=sys.stderr)
        return 2

    config = Config()
    try:
        source = skill_source(config, args.skill)
    except FileNotFoundError as error:
        print(f"{error.filename}: not found", file=sys.stderr)
        return 1
    # the gate on a skill: a label is written from the line saying what a skill is for, so a skill
    # whose own header yields none is dropped here rather than guessed at
    if not skill_description(source):
        print(f"{args.skill}: no description in its front matter", file=sys.stderr)
        return 1

    body = request_body(config.model, state(config, args.skill, source))
    if args.print_request:
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return 0

    if config.dry_run:
        output = placeholder()
    else:
        try:
            output = profile(Jev(config).ask(body))
        except (httpx.HTTPError, RuntimeError) as error:
            print(f"{args.skill}: {type(error).__name__}: {error}", file=sys.stderr)
            return 1
    written = write(config, args.skill, output)
    print(f"built {written}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
