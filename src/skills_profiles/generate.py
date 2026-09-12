"""DAG-driven generation; per-prompt files on disk act as the resume cache."""

import asyncio
import logging
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .config import Settings
from .data import read_skill_md, skill_md_path
from .images import cover_needed, covers_on_disk
from .models import SkillRecord
from .outputs import (
    load_index,
    read_prompt_output,
    write_index,
    write_prompt_output,
    write_stats,
)
from .prompts import PromptSet, PromptSpec, render_user_prompt

logger = logging.getLogger(__name__)


@dataclass
class RunStats:
    """Aggregated counters for one `run`, tallied by `run_all`.

    `prompts_stale` counts reused-cached outputs that failed schema validation
    and were regenerated; `skills_failed` counts skills whose generation raised
    (LLM quota/connection errors are isolated per skill and never abort the
    run); `llm_seconds` sums the per-prompt LLM seconds, so
    `llm_seconds / prompts_generated` is the average per-prompt latency (the
    sum can exceed the wall time, prompts run concurrently).
    """

    selected: int = 0  # skills handed to run_all
    skills_generated: int = 0
    skills_skipped: int = 0  # no SKILL.md in the snapshot
    skills_failed: int = 0  # generation raised; retried whole on the next run
    prompts_generated: int = 0
    prompts_reused: int = 0
    prompts_stale: int = 0
    llm_seconds: float = 0.0


def _tally(stats: RunStats, record: dict) -> None:
    """Fold one skill's record into the run stats."""
    if record.get("failed"):
        stats.skills_failed += 1
        return
    generated = record.get("generated", ())
    stats.skills_generated += 1 if generated else 0
    stats.skills_skipped += 1 if record.get("skipped") else 0
    stats.prompts_generated += len(generated)
    stats.prompts_reused += len(record["intros"]) - len(generated)
    stats.prompts_stale += len(record.get("stale", ()))
    stats.llm_seconds += sum(record.get("prompt_seconds", {}).values())


def _dump_messages(skill: SkillRecord, spec, messages: list[dict]) -> None:
    print(f"\n===== debug {skill.id} / {spec.id} =====", file=sys.stderr)
    for message in messages:
        print(f"----- {message['role']} -----", file=sys.stderr)
        print(message["content"], file=sys.stderr)


def _dump(outputs: dict[str, Any]) -> dict[str, Any]:
    """Every prompt output as a plain dict, keyed by prompt id."""
    return {pid: out.model_dump(mode="json") for pid, out in outputs.items()}


def _load_cached(
    settings: Settings, prompts: PromptSet, skill: SkillRecord, only: set[str] | None = None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Split the selection into (cached outputs, prompt ids still to generate, stale ids).

    A prompt belongs to the selection when it is in `prompts` and (with `only`)
    in the closure of the requested ids. Its stored json is trusted as-is, but
    must still validate against the current schema — missing prompts come back
    as pending, schema-stale ones as stale (also pending, but counted apart).
    """
    targets = prompts.closure_ids(only) if only is not None else set(prompts.by_id)
    outputs: dict[str, Any] = {}
    stale: list[str] = []
    for spec_id in prompts.ordered_ids():
        if spec_id not in targets:
            continue
        stored = read_prompt_output(settings, skill.id, spec_id)
        if stored is None:
            continue
        try:
            outputs[spec_id] = prompts.by_id[spec_id].output_model.model_validate(stored)
        except ValidationError:
            logger.debug("%s: stored %s no longer validates - regenerating", skill.id, spec_id)
            stale.append(spec_id)
    pending = [pid for pid in prompts.ordered_ids() if pid in targets and pid not in outputs]
    return outputs, pending, stale


def select_skills(
    settings: Settings,
    prompts: PromptSet,
    skills: list[SkillRecord],
    only: set[str] | None = None,
    limit: int | None = None,
) -> list[SkillRecord]:
    """The skills of this run: the first `limit` ones that still need work.

    "Work" is anything the run can complete for the skill: a missing prompt, or
    a cover recipe without its picture — `limit N` therefore means "make N
    skills complete", text and picture alike. Skills are considered in install
    order (the list handed in is already the `settings.total_limit` window, see
    `data.portfolio`); one that needs nothing is skipped without spending any
    of the budget, so repeated runs keep moving down the list instead of
    re-scanning the same head.
    Skills without a SKILL.md in the snapshot can never generate anything, so
    they are passed over the same way — otherwise they would sit at the head
    of the list and burn the budget on every run (the run_one-level skip stays
    as a fallback for callers that hand skills over directly).
    limit=None uses settings.limit; limit <= 0 selects every skill.
    """
    limit = settings.limit if limit is None else limit

    def _needs_work(skill: SkillRecord) -> bool:
        if not skill_md_path(settings, skill).is_file():
            return False
        return bool(_load_cached(settings, prompts, skill, only)[1]) \
            or cover_needed(settings, skill.id)

    if limit <= 0:
        return [s for s in skills if _needs_work(s)]
    picked: list[SkillRecord] = []
    for skill in skills:
        if len(picked) == limit:
            break
        if _needs_work(skill):
            picked.append(skill)
    return picked


def coverage(
    settings: Settings, prompts: PromptSet, skills: list[SkillRecord],
    only: set[str] | None = None,
) -> dict:
    """Cache coverage over all skills, for the run summary and stats.json.

    Applies the same cache rules as a run to every skill's stored outputs and
    returns {"skills", "profiled", "complete", "remaining", "prompts"}:
    `profiled` = every selected prompt is cached; `complete` = profiled and its
    cover is drawn too (the sense `--limit` spends budget on, see select_skills);
    `remaining` = skills a run would still work on; and, per prompt id, how many
    skills have it cached. Only called once per run: it re-reads every stored
    output.
    """
    targets = prompts.closure_ids(only) if only is not None else set(prompts.by_id)
    profiled = 0
    complete = 0
    per_prompt = dict.fromkeys(sorted(targets), 0)
    for skill in skills:
        outputs, pending, _ = _load_cached(settings, prompts, skill, only)
        if not pending:
            profiled += 1
            if not cover_needed(settings, skill.id):
                complete += 1
        for pid in outputs:
            per_prompt[pid] += 1
    return {
        "skills": len(skills),
        "profiled": profiled,
        "complete": complete,
        "remaining": len(skills) - complete,
        "prompts": per_prompt,
    }


def write_artifact_stats(settings: Settings, cov: dict) -> dict:
    """Overwrite output/stats.json with the artifact's current state.

    How complete the artifacts are right now: skills profiled (text) and complete
    (text + cover), a cached count per prompt, covers rendered. Nothing a run did
    (counters, timings) and no provenance — when this snapshot was published and
    which mirror tag its dataset came from are stamped into the same file by the
    publish step, the only actor that can know both (see the publish-dist action).
    `cov` is the coverage dict computed by the caller; the full stats written are
    returned.
    """
    stats = {
        "skills": {"total": cov["skills"], "profiled": cov["profiled"],
                   "complete": cov["complete"]},
        "prompts": cov["prompts"],
        # rendered covers are counted from disk too: prompts.cover says how many
        # recipes exist, this says how many of them have become a picture
        "covers": {"rendered": covers_on_disk(settings)},
    }
    write_stats(settings, stats)
    return stats


async def run_prompt(
    llm, settings: Settings, prompts: PromptSet, spec: PromptSpec, skill: SkillRecord, deps: dict,
    debug: bool = False,
) -> Any:
    messages = [
        {"role": "system", "content": prompts.render_system_prompt(skill)},
        {"role": "user", "content": render_user_prompt(spec, deps)},
    ]
    if debug:
        _dump_messages(skill, spec, messages)
    return await llm.create(
        model=settings.model,
        response_model=spec.output_model,
        messages=messages,
        max_retries=settings.max_retries,
    )


async def run_one(
    llm, settings: Settings, prompts: PromptSet, skill: SkillRecord,
    only: set[str] | None = None, debug: bool = False,
    sem: asyncio.Semaphore | None = None,
) -> tuple[dict, bool]:
    """Generate one skill's profiles; returns (record, reused).

    Storage: each prompt's output is its own <prompt_id>.json under the skill's
    artifact dir, committed (json + md/ copy) right after it is generated, so a
    crash keeps every completed prompt. `run_all` records the skills that
    generated something in skills.jsonl, the index `invalidate --stale`
    compares against — a fully cached run leaves the disk untouched.

    Cache rule: an existing per-prompt json is trusted as-is (invalidation is
    `sync`'s and `invalidate`'s job), but every reused output must still
    validate against its current schema — missing or invalid prompts are
    regenerated, and prompts outside the selection (`only`, plus the closure of
    their dependencies) are simply not touched.

    The skill's SKILL.md is read from the local snapshot only once something has
    to be generated, so a fully cached skill reads nothing at all.

    The skill's prompts run concurrently where the DAG allows: every prompt
    waits for its dependencies' tasks, then takes a slot from `sem` — the same
    pool `run_all` shares across skills (a fresh one from settings.concurrency
    when called standalone). Nothing is generated outside the pool.

    The record carries run-bookkeeping besides the outputs: `generated` (prompt
    ids newly generated), `stale` (of those, ids whose cache was schema-stale),
    `seconds` (wall time of the generation phase), `prompt_seconds` (per-prompt
    LLM seconds) and `skipped` (no SKILL.md).
    """
    outputs, generated, stale = _load_cached(settings, prompts, skill, only)
    if not generated:
        return {"skill": skill.model_dump(), "intros": _dump(outputs)}, True

    skill_md = read_skill_md(settings, skill)
    if skill_md is None:
        logger.warning("%s: no SKILL.md in the snapshot - skipped", skill.id)
        return {"skill": skill.model_dump(), "intros": _dump(outputs), "skipped": True}, True
    skill = skill.model_copy(update={"skill_md": skill_md})

    sem = sem or asyncio.Semaphore(settings.concurrency)
    tasks: dict[str, asyncio.Task] = {}

    async def generate(spec_id: str) -> float:
        """One prompt: wait for its deps' tasks, then take a concurrency slot."""
        spec = prompts.by_id[spec_id]
        await asyncio.gather(*(tasks[d] for d in spec.depends_on if d in tasks))
        deps = {d: outputs[d] for d in spec.depends_on}
        async with sem:
            start = time.monotonic()
            outputs[spec_id] = await run_prompt(
                llm, settings, prompts, spec, skill, deps, debug=debug)
            write_prompt_output(settings, skill.id, spec_id,
                                outputs[spec_id].model_dump(mode="json"))
            return time.monotonic() - start

    for spec_id in generated:  # topologically ordered; deps resolve via the tasks
        tasks[spec_id] = asyncio.create_task(generate(spec_id))
    start = time.monotonic()
    try:
        durations = await asyncio.gather(*tasks.values())
    except BaseException:
        for task in tasks.values():
            task.cancel()
        await asyncio.gather(*tasks.values(), return_exceptions=True)
        raise

    return {
        "skill": skill.model_dump(),
        "intros": _dump(outputs),
        "generated": generated,
        "stale": stale,
        "seconds": time.monotonic() - start,
        "prompt_seconds": dict(zip(generated, durations, strict=True)),
    }, False


async def run_all(
    llm,
    settings: Settings,
    skills: list[SkillRecord],
    prompts: PromptSet,
    on_skill_done: Callable[[SkillRecord, dict, bool], None] | None = None,
    only: set[str] | None = None,
    debug: bool = False,
    stats: RunStats | None = None,
) -> list[dict]:
    """Generate profiles for all skills concurrently.

    One semaphore bounds the whole run: at most `settings.concurrency` LLM
    calls in flight, shared across skills and across the prompts of each skill
    (see run_one). Skills whose every requested prompt is already cached and
    valid are skipped; `only` narrows work to a subset of prompts. A skill
    whose generation raises (quota, connection, ...) is isolated: the error is
    logged, its completed prompts stay on disk, and the run continues — a
    failed skill keeps all its prompts pending for the next run. When anything
    was generated, skills.jsonl is updated once, at the end. When `stats` is
    given, the run's counters are tallied into it. An unknown id in `only` is
    a caller error, not a skill failure: it raises KeyError before any work.
    """
    if only is not None and (unknown := only - prompts.by_id.keys()):
        raise KeyError(f"unknown prompt(s) {sorted(unknown)}")
    sem = asyncio.Semaphore(settings.concurrency)

    async def _one(skill: SkillRecord) -> dict:
        try:
            record, reused = await run_one(llm, settings, prompts, skill, only, debug, sem=sem)
        except Exception as e:
            logger.error("%s: generation failed, continuing with the rest: %s", skill.id, e)
            record, reused = {"skill": skill.model_dump(), "failed": True}, False
        if on_skill_done:
            on_skill_done(skill, record, reused)
        if stats is not None:
            _tally(stats, record)
        return record

    records = await asyncio.gather(*(_one(s) for s in skills))
    _update_index(settings, records)
    return records


def _update_index(settings: Settings, records: list[dict]) -> None:
    """Record the generation-time hash of every skill that generated something.

    The hash is the freshness record `invalidate --stale` compares against the
    snapshot; a run that generated nothing writes nothing. Aggregated prompt
    outputs (domain, persona, ...) are not written here: write_index derives
    them from the per-prompt json on disk, so index lines cannot drift from
    what is actually stored.
    """
    fresh = [r for r in records if r.get("generated")]
    if not fresh:
        return
    index = load_index(settings)
    for record in fresh:
        skill_id = record["skill"]["id"]
        line = index.get(skill_id) or {}
        line["hash"] = record["skill"]["hash"]
        index[skill_id] = line
    write_index(settings, index)
