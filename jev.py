#!/usr/bin/env python3
"""The System One angles: `domain`, answered by Jev over 302.AI rather than by a chat model.

Its endpoint is not OpenAI-compatible - a `state` and typed `questions` in, typed `answers` out,
and no free text at all - so the request is built here and never reaches `gen.py`. Everything else
is shared with it: the same system message as the state, the same `profiles/<id>/<angle>.json` and
markdown copy, the same writer.

    jev.py --angles                    the angles the batch hands to this script, not to gen.py
    jev.py <angle> <skill> [--print]   build one cell, or print the request and call nothing

Driven by the justfile, which sends a pair to whichever of the two producers owns the angle.
"""

import argparse
import json
import sys
import time

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict

import gen

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
# Everything narrower lives in CRITERIA, beside the category it draws a line around - a rule that
# only restates this one for one pair of categories belongs in the criteria of whichever of the two
# it excludes from, never here. The rule is measured: without it the endpoint read skills by the
# medium they work through, calling every CLI and API wrapper `development` (12 of the 17
# disagreements in a 100-skill A/B) and answering `education` for tools that interview a developer.
# Both of those were the criteria's fault, not the rule's: `development` listed nothing before the
# code was written, and `education` named interviews.
INSTRUCTION = (
    "Which single category does this skill primarily belong to?\n"
    "1. Judge what the skill is for, not how it works or what it is written in: the interface it "
    "uses - a script, a CLI, an API wrapper - is not its category, and a tool that draws, watches "
    "or writes belongs to the category of what it produces.\n"
    "2. When several categories fit, choose the one the skill's main output serves.")
# What each angle asks: every question of the one call, all answered against the same state. The
# names here are the only list of this script's angles there is - `--angles` is how the batch reads
# it, so an angle added to it is an angle the batch builds, with no other file to keep in step.
QUESTIONS = {"domain": {"type": "choice", "instructions": INSTRUCTION, "criteria": CRITERIA}}


class JevConfig(BaseSettings):
    """This endpoint's own settings, under their own prefix: `.env` holds both this and gen's."""

    model_config = SettingsConfigDict(
        env_prefix="SKILLS_PROFILES_JEV_", env_file=".env", env_file_encoding="utf-8",
        extra="ignore", env_ignore_empty=True)

    api_key: str | None = None
    base_url: str = BASE_URL
    # an alias rather than a version: pin `jev-1.13.0` to keep a threshold meaning the same thing
    model: str = "jev-latest"
    # the endpoint answers in one to three seconds, and a dropped request never answers at all, so
    # the timeout is what decides how long a dead call waits before the retry that rescues it
    timeout: float = 20.0
    max_retries: int = 3


def request(model: str, state: str, questions: dict) -> dict:
    """The one body this endpoint takes: a state, the questions about it, and no messages."""
    return {"model": model, "state": state, "questions": questions}


def worth_retrying(error: httpx.HTTPError) -> bool:
    """A dropped connection or a busy gateway is worth the next try; a rejected body is not."""
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in {429, 500, 502, 503, 504}
    return True  # a timeout or a transport error never reached an answer


class Jev:
    """One `POST /v1/systemone`: a state, typed questions, typed answers, and no text."""

    def __init__(self, config: JevConfig, client: httpx.Client | None = None):
        if not config.api_key:
            raise SystemExit("SKILLS_PROFILES_JEV_API_KEY is not set - nothing to call with")
        self.config = config
        self.client = client or httpx.Client(timeout=config.timeout)

    def ask(self, body: dict) -> dict:
        """The questions against the state, in one call: the answers back.

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
    """How sure the endpoint says it is, or nothing when the answer does not carry one.

    It is derived from the distribution rather than being the probability of the option picked -
    the endpoint's own reading of how close the call was - which is what makes it worth keeping:
    it is how the labels worth a second look can be found without asking anyone again.
    """
    value = answer.get("confidence") if isinstance(answer, dict) else None
    return float(value) if isinstance(value, (int, float)) else None


def probabilities(answer: object) -> dict:
    """The distribution the choice was read off: every option of the enum, and the mass it holds.

    Kept whole, because it is the answer rather than a summary of it - a call decided 0.52 to 0.48
    says something a call decided 0.99 to 0.01 does not, and neither can be recovered from the
    winner. What narrows is the catalog: one category and one number, which are the two things a
    consumer filters on.
    """
    value = answer.get("probabilities") if isinstance(answer, dict) else None
    return dict(value) if isinstance(value, dict) else {}


def questions(angle: str) -> dict:
    return {angle: QUESTIONS[angle]}


def profile(answers: dict) -> dict:
    """Jev's answer as the profile's json: the category it chose, how sure it was, and the rest.

    The whole answer, the way another angle's file is the whole of its schema's output - and no
    reason line and no list, those being the two things this path does not have. `domain` is one
    member of the enum so that a consumer can filter on it; the category that came second is in
    `probabilities` with all the others, rather than being named beside it. The guard on the way in
    is the decoder this path no longer has: the request used to enforce the enum, so it is checked.
    """
    answer = answers.get("domain")
    picked = choice(answer)
    if picked not in CRITERIA:
        raise RuntimeError(f"chose {picked!r}, which is not a category")
    return {"domain": picked, "confidence": confidence(answer),
            "probabilities": probabilities(answer)}


def placeholder(angle: str) -> dict:
    """A value shaped like the answer, so `just dry=1` still writes the real layout."""
    first = next(iter(CRITERIA))
    return {angle: first, "confidence": 1.0,
            "probabilities": {name: 1.0 if name == first else 0.0 for name in CRITERIA}}


def state(config: gen.Config, skill: str, source: str) -> str:
    """The system message: the same bytes gen.py sends, so both producers read a skill alike."""
    template = (config.prompts_dir / gen.SYSTEM_MD).read_text(encoding="utf-8").strip()
    return gen.render(template, gen.skill_body(source), gen.skill_description(source), skill)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build one System One angle for one skill.")
    parser.add_argument("--angles", action="store_true",
                        help="print the angles this script builds, one per line, and stop")
    parser.add_argument("angle", nargs="?", help="the angle to build")
    parser.add_argument("skill", nargs="?", help="skill directory in the snapshot: owner/repo/slug")
    parser.add_argument("--print", dest="print_request", action="store_true",
                        help="print the request and stop, calling nothing")
    args = parser.parse_args(argv)

    if args.angles:
        print("\n".join(QUESTIONS))
        return 0
    if args.angle is None or args.skill is None or args.angle not in QUESTIONS:
        print(f"usage: jev.py <angle> <skill>   (angles: {', '.join(QUESTIONS)})", file=sys.stderr)
        return 2

    config = gen.Config()
    try:
        source = gen.skill_source(config, args.skill)
    except FileNotFoundError as error:
        print(f"{error.filename}: not found", file=sys.stderr)
        return 1
    # the same gate gen.py applies: a profile is written from the line saying what a skill is for,
    # so a skill whose own header yields none is dropped here rather than guessed at
    if not gen.skill_description(source):
        print(f"{args.skill}: no description in its front matter", file=sys.stderr)
        return 1
    settings = JevConfig()
    body = request(settings.model, state(config, args.skill, source), questions(args.angle))
    if args.print_request:
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return 0

    if config.dry_run:
        output = placeholder(args.angle)
    else:
        try:
            output = profile(Jev(settings).ask(body))
        except (httpx.HTTPError, RuntimeError) as error:
            print(f"{args.skill}: {type(error).__name__}: {error}", file=sys.stderr)
            return 1
    written = gen.write(config, args.angle, args.skill, output)
    print(f"built {written}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
