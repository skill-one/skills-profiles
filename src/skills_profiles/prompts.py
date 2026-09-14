"""Prompt DAG loaded from one markdown file per prompt in a prompts/ directory.

Each `<id>.md` has YAML frontmatter (description, output, depends_on) followed by
the user-prompt template as the body; the prompt id is the file name (stem).
`_system.md` holds the shared system prompt as a per-skill template: it renders
the skill context (name, description, SKILL.md source) every text prompt sees.

Templates are rendered with jinja2; the DAG is ordered with the stdlib
graphlib.TopologicalSorter. The prompts directory defaults to `./prompts` and
can be overridden with SKILLS_PROFILES_PROMPTS_DIR.
"""

from dataclasses import dataclass, field
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, TemplateSyntaxError
from pydantic import BaseModel

from .models import (
    BlackBoxIntro,
    Domain,
    DomainClassification,
    IntroText,
    Persona,
    SkillComments,
    Taglines,
    WhiteBoxIntro,
)

# frontmatter `output` name -> pydantic schema in models.py
OUTPUT_MODELS: dict[str, type[BaseModel]] = {
    cls.__name__: cls
    for cls in (DomainClassification, IntroText, BlackBoxIntro, WhiteBoxIntro,
                Taglines, Persona, SkillComments)
}

# Template contexts. System prompt (per skill): `skill` (SkillRecord) and
# `skill_md` (its source text). User prompts: `deps` (dict of prompt_id ->
# parsed output of upstream prompts), `domain_taxonomy` (rendered
# '- name: description' lines from models.Domain).


@dataclass(frozen=True)
class PromptSpec:
    id: str
    description: str
    output_model: type[BaseModel]
    template: str
    depends_on: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class PromptSet:
    """All prompts loaded from one directory, plus the shared system template."""

    directory: Path
    system_template: str
    by_id: dict[str, PromptSpec]

    def render_system_prompt(self, skill: Any) -> str:
        """The shared system prompt for one skill: identity + SKILL.md source."""
        return _env.from_string(self.system_template).render(
            skill=skill, skill_md=skill.skill_md
        )

    def ordered_ids(self) -> list[str]:
        """Topologically ordered prompt ids; raises CircularDependencyError on bad DAG."""
        sorter = TopologicalSorter({p.id: set(p.depends_on) for p in self.by_id.values()})
        return list(sorter.static_order())

    def closure_ids(self, ids: set[str]) -> set[str]:
        """The given ids plus every transitive dependency needed to run them."""
        seen: set[str] = set()
        stack = list(ids)
        while stack:
            pid = stack.pop()
            if pid in seen:
                continue
            seen.add(pid)
            stack.extend(self.by_id[pid].depends_on)
        return seen


def _parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: prompt files must start with '---' frontmatter")
    _, meta, body = text.split("---", 2)
    return yaml.safe_load(meta) or {}, body.strip()


def _validate_template(source: str, name: str) -> None:
    """Parse eagerly so a syntax error (e.g. markdown-escaped `\\_` pasted into a
    variable like `{{ skill\\_md }}`) names the file at load time, not mid-run."""
    try:
        _env.parse(source)
    except TemplateSyntaxError as e:
        raise ValueError(f"{name}: invalid jinja2 template, line {e.lineno}: {e.message}") from e


def _load_prompt(path: Path) -> PromptSpec:
    meta, template = _parse_frontmatter(path)
    output_name = meta.get("output")
    if output_name not in OUTPUT_MODELS:
        raise ValueError(f"{path.name}: unknown output model {output_name!r}")
    _validate_template(template, path.name)
    return PromptSpec(
        id=path.stem,
        description=meta.get("description", ""),
        output_model=OUTPUT_MODELS[output_name],
        template=template,
        depends_on=frozenset(meta.get("depends_on") or []),
    )


def load_prompt_set(directory: Path) -> PromptSet:
    directory = Path(directory)
    by_id: dict[str, PromptSpec] = {}
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        spec = _load_prompt(path)
        if spec.id in by_id:
            raise ValueError(f"duplicate prompt id {spec.id!r}")
        by_id[spec.id] = spec
    if not by_id:
        raise ValueError(f"no prompt files found in {directory}")
    for spec in by_id.values():
        unknown = spec.depends_on - by_id.keys()
        if unknown:
            raise ValueError(f"{spec.id}: depends on unknown prompts {sorted(unknown)}")
    system_template = (directory / "_system.md").read_text(encoding="utf-8").strip()
    _validate_template(system_template, "_system.md")
    return PromptSet(
        directory=directory,
        system_template=system_template,
        by_id=by_id,
    )


_env = Environment(autoescape=False, keep_trailing_newline=True)


def render_user_prompt(spec: PromptSpec, deps: dict[str, Any]) -> str:
    """Render the user prompt for one spec; `deps` maps prompt_id -> parsed output."""
    return _env.from_string(spec.template).render(
        deps=deps, domain_taxonomy=Domain.taxonomy_text(),
    )
