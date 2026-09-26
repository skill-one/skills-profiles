#!/usr/bin/env python3
"""Label one skill's `domain` with Jev (TypeSafe System One) over its own API.

The domain angle. Its endpoint is not OpenAI-compatible - a `state` and typed `questions` in,
typed `answers` out, and no free text. The state is rendered from `prompts/_system.md`: the
skill's name, the description out of its own front matter, its `SKILL.md` body, and - the one extra
layer `domain` gets - the sibling skills beside it in its repository, a category being a property
of the repository rather than of one file.

    jev.py <skill> [--print]   label one skill, or print the request and call nothing

Everything else - the tree, the source, the call's retries, the write and the command - is shared
in `common.py`. Driven by the justfile, one process per skill.
"""

import httpx

import common
from common import Config

SYSTEM_MD = "_system.md"

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


def state(config: Config, skill: str, source: str) -> str:
    """The system message, rendered from the one template, plus the repository disambiguation."""
    template = common.load_prompt(config, SYSTEM_MD)
    return common.render(template, skill_body=common.skill_body(source),
                         description=common.skill_description(source), name=skill,
                         repo=common.repository(config, skill))


def request_body(model: str, state_text: str) -> dict:
    """The one body this endpoint takes: a state, the question about it, and no messages."""
    return {"model": model, "state": state_text, "questions": QUESTION}


class Jev:
    """One `POST /v1/systemone`: a state, a typed question, a typed answer, and no text."""

    def __init__(self, config: Config, client: httpx.Client | None = None):
        key = config.api_key
        if not key:
            raise SystemExit("SKILLS_PROFILES_API_KEY is not set - nothing to call with")
        self.config = config
        self.api_key = key
        self.client = client or httpx.Client(timeout=config.timeout)

    def ask(self, body: dict) -> dict:
        """The question against the state, in one call: the typed answers back."""
        payload = common.post_json(self.client, self.config.base_url, self.api_key, body,
                                  self.config.max_retries)
        return payload.get("answers", {}) if isinstance(payload, dict) else {}


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
    answer = answers.get(common.DOMAIN_ANGLE)
    picked = choice(answer)
    if picked not in CRITERIA:
        raise RuntimeError(f"chose {picked!r}, which is not a category")
    return {"domain": picked, "confidence": confidence(answer),
            "probabilities": probabilities(answer)}


def placeholder(_description: str) -> dict:
    """A value shaped like the answer, so `just dry=1` still writes the real layout."""
    first = next(iter(CRITERIA))
    return {"domain": first, "confidence": 1.0,
            "probabilities": {name: 1.0 if name == first else 0.0 for name in CRITERIA}}


def _request(config: Config, skill: str, source: str, _description: str) -> dict:
    return request_body(config.model, state(config, skill, common.cap_source(source)))


def _produce(config: Config, body: dict, _source: str) -> dict:
    return profile(Jev(config).ask(body))


def main(argv: list[str] | None = None) -> int:
    return common.run(
        argv, program="jev.py", description="Label one skill's domain.",
        angle=common.DOMAIN_ANGLE, build_request=_request, produce=_produce,
        placeholder=placeholder)


if __name__ == "__main__":
    raise SystemExit(main())
