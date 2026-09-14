"""On-disk artifact layout under <output_dir>: one json per prompt in
skills/<id>/ (with a markdown copy in md/), the binary assets a prompt owns
beside it (the cover prompt's rendered png), plus skills.jsonl — the skill
index, one line per skill carrying its id, the upstream content hash its
profiles were generated from, and the aggregated domain/persona outputs."""

import json
import logging
import shutil
from collections.abc import Iterable, Mapping
from pathlib import Path

from .config import Settings
from .layout import INDEX_NAME, MD_SUBDIR, SKILLS_SUBDIR
from .models import Domain

AGGREGATED_PROMPTS = ("domain", "persona")  # prompts folded into the index lines, derived from disk
# asset filenames (relative to a skill's artifact dir) owned by a prompt: they
# are its rendered artifacts, so invalidating the prompt drops them with the
# json (see invalidate). The cover recipe owns cover.png — the picture is
# rendered from the recipe's text, and invalidating the recipe drops both.
PROMPT_ASSETS: dict[str, tuple[str, ...]] = {"cover": ("cover.png",)}

logger = logging.getLogger(__name__)


def skill_result_dir(settings: Settings, skill_id: str) -> Path:
    """Per-skill artifacts live under <output_dir>/skills/<owner>/<repo>/<slug>/
    (id-based, mirroring the upstream data/skills/ layout)."""
    return settings.output_dir / SKILLS_SUBDIR / skill_id.replace(":", "_")


def prompt_result_path(settings: Settings, skill_id: str, prompt_id: str) -> Path:
    """The json file holding one prompt's structured output."""
    return skill_result_dir(settings, skill_id) / f"{prompt_id}.json"


def prompt_markdown_path(settings: Settings, skill_id: str, prompt_id: str) -> Path:
    """The markdown copy of one prompt's output; kept in a `md/` subdir so the
    json directory itself only holds a prompt's own artifacts."""
    return skill_result_dir(settings, skill_id) / MD_SUBDIR / f"{prompt_id}.md"


def index_path(settings: Settings) -> Path:
    """The skill index: one json line per generated skill."""
    return settings.output_dir / INDEX_NAME


def load_index(settings: Settings) -> dict[str, dict]:
    """skill id -> its index line ({id, hash, domain?, persona?}); {} when unknown."""
    try:
        text = index_path(settings).read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    index: dict[str, dict] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            logger.warning("Skipping unreadable index line: %s", line[:80])
            continue
        index[entry["id"]] = entry
    return index


def write_index(settings: Settings, index: Mapping[str, dict]) -> None:
    """Rewrite the whole index, one line per skill, sorted by skill id.

    A line is a projection, not a cache: `id` and the generation-time `hash`
    come from `index` (the freshness record `invalidate --stale` compares
    against), while every aggregated prompt output in AGGREGATED_PROMPTS is
    recomputed from the per-prompt json on disk — so a line can never drift
    from what is actually stored, and lines written before an aggregated
    prompt existed (or after its json vanished) heal on the next rewrite.
    Keys follow a fixed order — id, hash, domain, persona, then anything
    else — so lines stay grep-able and diffs stable regardless of how a line
    was built.
    """
    path = index_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(_ordered_line(settings, sid, index[sid]), ensure_ascii=False) + "\n"
                for sid in sorted(index)),
        encoding="utf-8",
    )


def _ordered_line(settings: Settings, skill_id: str, line: Mapping) -> dict:
    """One index line in canonical key order, its aggregated prompt outputs
    re-derived from disk."""
    ordered: dict = {"id": skill_id}
    if "hash" in line:
        ordered["hash"] = line["hash"]
    for key in AGGREGATED_PROMPTS:
        stored = read_prompt_output(settings, skill_id, key)
        if stored is not None:
            ordered[key] = stored
    ordered.update({k: v for k, v in line.items()
                    if k not in ordered and k not in AGGREGATED_PROMPTS})
    return ordered


def read_prompt_output(settings: Settings, skill_id: str, prompt_id: str) -> dict | None:
    """One prompt's stored json as a dict, or None when absent or unreadable."""
    try:
        return json.loads(
            prompt_result_path(settings, skill_id, prompt_id).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_hashes(settings: Settings) -> dict[str, str]:
    """skill id -> the hash its profiles were generated from; {} when unknown."""
    return {sid: line.get("hash", "") for sid, line in load_index(settings).items()}


def write_stats(settings: Settings, stats: Mapping) -> Path:
    """Overwrite output/stats.json: the artifact's current state, not the run's.

    How many skills are complete and how many hold each prompt's output on disk,
    plus how many covers are rendered. Run counters and timings stay out of it,
    and so does provenance: the publish step stamps `publishedAt` and the
    `upstream` mirror tag into this same file (see the publish-dist action),
    because only it knows both — a value copied here by a run would lag the day
    `sync` republished the dataset without regenerating anything. One snapshot
    file (no history) so CI and humans read the same place; sorting dict keys
    keeps the layout stable across runs.
    """
    path = settings.output_dir / "stats.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def write_prompt_output(settings: Settings, skill_id: str, prompt_id: str, output: dict) -> Path:
    """Write one prompt's output as json in the skill dir + a markdown copy in md/.

    Markdown first, json last: the json is the commit marker, so a crash can
    only leave a stray markdown (regenerated together with the json next run),
    never a valid-looking json without its markdown.
    """
    skill_dir = skill_result_dir(settings, skill_id)
    md_path = prompt_markdown_path(settings, skill_id, prompt_id)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_render_markdown(skill_id, prompt_id, output), encoding="utf-8")
    (skill_dir / f"{prompt_id}.json").write_text(
        json.dumps(output, ensure_ascii=False), encoding="utf-8"
    )
    return skill_dir


def invalidate(settings: Settings, skill_ids: Iterable[str] | None = None,
               prompt_ids: Iterable[str] | None = None,
               assets_only: bool = False) -> int:
    """Delete cached prompt outputs (and the assets they own) so the next run refills them.

    `skill_ids` None means every skill on record; `prompt_ids` None
    means every prompt of each selected skill. Dropping a prompt also drops
    every prompt downstream of it in the DAG (the cover recipe derives from the
    persona, so a new tool name must not keep the old recipe), and the rendered
    assets the dropped prompts own (PROMPT_ASSETS) — which is how a cover gets
    re-rendered: one invalidation, then `run` refills the jsons and the picture.
    With `assets_only` the cached outputs all stay and only their rendered
    assets are dropped (no dependent cascade, no index change): the next `run`
    re-renders them from the recipes already on disk.
    A skill left without any output is dropped from the index, i.e. it
    counts as new again; the index is then rewritten so its aggregated copies
    match what is left on disk. This is the only invalidation path:
    `invalidate --stale` uses it for skills whose upstream hash changed. Returns
    the number of removed prompt outputs and assets.
    """
    index = load_index(settings)
    targets = sorted(index) if skill_ids is None else list(dict.fromkeys(skill_ids))
    if prompt_ids is not None and not assets_only:
        prompt_ids = _with_dependents(settings, set(prompt_ids))  # a dropped prompt takes its dependents with it
    removed = 0
    dropped = False
    for skill_id in targets:
        paths = (_stored_jsons(settings, skill_id) if prompt_ids is None
                 else [prompt_result_path(settings, skill_id, p) for p in prompt_ids])
        for path in paths:
            for asset in PROMPT_ASSETS.get(path.stem, ()):  # explicit filenames in the skill dir
                removed += _unlink(path.parent / asset)
            if assets_only:  # the cached output stays; only its rendered asset went
                continue
            _unlink(path.parent / MD_SUBDIR / f"{path.stem}.md")
            removed += _unlink(path)
        if not _stored_jsons(settings, skill_id):
            shutil.rmtree(skill_result_dir(settings, skill_id), ignore_errors=True)
            dropped |= index.pop(skill_id, None) is not None
    if removed or dropped:
        write_index(settings, index)
    return removed


def _with_dependents(settings: Settings, prompt_ids: set[str]) -> set[str]:
    """`prompt_ids` plus every prompt that transitively depends on one of them.

    Read from the prompt DAG (prompts/ frontmatter), so invalidating an upstream
    output never leaves a downstream one stale on disk.
    """
    from .prompts import load_prompt_set  # imported here: prompts.py has no use for outputs.py

    by_id = load_prompt_set(settings.prompts_dir).by_id
    dependents: dict[str, set[str]] = {pid: set() for pid in by_id}
    for spec in by_id.values():
        for dep in spec.depends_on:
            dependents[dep].add(spec.id)
    seen = set(prompt_ids)
    stack = list(prompt_ids)
    while stack:
        for child in dependents.get(stack.pop(), ()):
            if child not in seen:
                seen.add(child)
                stack.append(child)
    return seen


def _stored_jsons(settings: Settings, skill_id: str) -> list[Path]:
    """The prompt jsons cached for one skill."""
    return sorted(skill_result_dir(settings, skill_id).glob("*.json"))


def _unlink(path: Path) -> int:
    """Remove a file if present; 1 when something was removed."""
    try:
        path.unlink()
    except FileNotFoundError:
        return 0
    return 1


def _render_markdown(skill_id: str, prompt_id: str, output: dict) -> str:
    name = skill_id.rsplit("/", 1)[-1]
    lines = [f"# {name} (`{skill_id}`)", "", f"## {prompt_id}", ""]
    lines += _render_output(output)
    return "\n".join(lines).rstrip() + "\n"


def _render_output(output: dict) -> list[str]:
    """Generic markdown rendering: lists become bullets, strings become paragraphs."""
    lines: list[str] = []
    for key, value in output.items():
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                for item in value:
                    lines.append(f"- {_render_dict(item)}")
            else:
                lines.extend(f"- {item}" for item in value)
        elif isinstance(value, dict):
            lines.append(_render_dict(value))
        elif len(output) > 1:
            if isinstance(value, str):
                value = Domain.display(value)  # known domain values get their emoji
            lines.append(f"**{key}**: {value}")
        else:
            lines.append(str(value))
        lines.append("")
    return lines


def _render_dict(d: dict) -> str:
    """Render a dict as 'key: value, key: value'."""
    return ", ".join(f"{k}: {v}" for k, v in d.items())
