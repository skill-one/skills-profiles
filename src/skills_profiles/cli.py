"""Typer CLI: sync / invalidate / run."""

import asyncio
import logging
import time
from collections.abc import Callable

import typer

from .config import Settings
from .data import load_skills, portfolio, stale_result_ids, sync_data
from .generate import RunStats, coverage, run_all, select_skills, write_artifact_stats
from .images import CoverStats, FakeImages, cover_needed, make_images, run_covers
from .llm import FakeLLM, make_llm
from .logging import setup_logging
from .models import SkillRecord
from .outputs import invalidate as invalidate_cache
from .outputs import load_hashes
from .prompts import PromptSet, load_prompt_set

logger = logging.getLogger(__name__)

app = typer.Typer(help="Generate multi-angle Chinese profiles for agent skills.")


def cover_progress(total: int) -> Callable[[SkillRecord, int | None], None]:
    """The per-skill logger of `run`'s rendering post-pass."""
    done = 0

    def on_done(_skill: SkillRecord, written: int | None) -> None:
        nonlocal done
        done += 1
        if written is None:
            detail = "(failed)"
        elif written >= 1_048_576:
            detail = f"{written / 1_048_576:.1f} MB"
        else:
            detail = f"{written / 1024:.0f} KB"
        logger.info("  [%d/%d] %s: %s", done, total, _skill.id, detail)

    return on_done


def served_skills(settings: Settings) -> tuple[list[SkillRecord], list[SkillRecord]]:
    """The whole snapshot plus its window (`data.portfolio`) over it.

    The full list is returned so hash comparison can still see a skill that has
    slipped outside the window (it exists upstream, so it is not stale); the
    windowed list is where `run` starts, so the one dataset ceiling
    (`SKILLS_PROFILES_TOTAL_LIMIT`) bounds profiles and pictures alike. The cap
    is only announced when it trims.
    """
    every_skill = load_skills(settings)
    skills = portfolio(settings, every_skill)
    if len(skills) < len(every_skill):
        logger.info("Serving the top %d of %d installed skills (total_limit=%d); "
                    "the rest are never profiled or drawn",
                    len(skills), len(every_skill), settings.total_limit)
    return every_skill, skills


def parse_prompt_ids(prompt_set: PromptSet, raw: str | None) -> set[str] | None:
    """The `--prompts` value as a validated set; None means "every prompt".

    Shared by `run` and `invalidate` so the two agree on what a selection is,
    and an unknown id is reported with the available ones instead of failing
    later, mid-run.
    """
    if not raw:
        return None
    ids = {p.strip() for p in raw.split(",") if p.strip()}
    unknown = ids - set(prompt_set.by_id)
    if unknown:
        raise typer.BadParameter(
            f"unknown prompt(s) {sorted(unknown)}; available: {sorted(prompt_set.by_id)}"
        )
    return ids


@app.command()
def sync(
    refresh: bool = typer.Option(
        False, "--refresh",
        help="Download the snapshot again even when it is already the newest tag",
    ),
) -> None:
    """Download the newest dist snapshot (skills.jsonl + every SKILL.md) as one
    tarball into the data dir. Sync never touches the generated results; invalidating
    stale ones is `invalidate --stale`'s explicit job.

    Upstream tags each daily scrape; a sync whose tag is already on disk does
    nothing, so repeat syncs cost one small request instead of a download.
    """
    setup_logging()
    try:
        report = sync_data(Settings(), refresh)
    except RuntimeError as e:
        logger.error("%s", e)
        raise typer.Exit(1) from e
    fetched = (f"downloaded {report.tag} in {report.seconds:.1f}s" if report.downloaded
               else f"already at {report.tag}")
    typer.echo(f"Dataset ready at {report.data_dir} ({fetched})")


@app.command()
def invalidate(
    skill: list[str] = typer.Option(
        None, "--skill", help="Skill id to invalidate; repeatable. Omit for every skill"
    ),
    prompts_opt: str | None = typer.Option(
        None, "--prompts", help="Comma-separated prompt ids; omit for every prompt"
    ),
    all_skills: bool = typer.Option(
        False, "--all", help="Allow invalidating every skill (required when no filter is given)"
    ),
    stale: bool = typer.Option(
        False, "--stale",
        help="Select every cached skill whose upstream content hash changed or that "
             "vanished from the snapshot (run `sync` first to have a fresh snapshot)",
    ),
) -> None:
    """Drop cached outputs so the next `run` regenerates them."""
    setup_logging()
    settings = Settings()

    prompt_ids: set[str] | None = None
    if prompts_opt:
        prompt_ids = parse_prompt_ids(load_prompt_set(settings.prompts_dir), prompts_opt)

    skill_ids = list(skill or [])
    if stale:
        found = stale_result_ids(settings)
        logger.info("%d stale skill(s): upstream content changed or skill gone", len(found))
        skill_ids = list(dict.fromkeys(skill_ids + found))
        if not found:
            logger.info("Nothing to invalidate")
            return
    if not skill_ids and not prompt_ids and not all_skills:
        raise typer.BadParameter("refusing to invalidate everything - pass --all to confirm")

    recorded = load_hashes(settings)
    for skill_id in skill_ids:
        if skill_id not in recorded:
            logger.warning("%s has no cached results", skill_id)
    removed = invalidate_cache(settings, skill_ids or None, prompt_ids)
    targets = sorted(skill_ids) if skill_ids else sorted(recorded)
    logger.info("Invalidated %d output(s) across %d skill(s)", removed, len(targets))


@app.command()
def run(
    limit: int | None = typer.Option(
        None, "--limit",
        help="How many skills to complete this run, most installed first "
             "(0 = every skill with gaps). A skill is complete when every prompt "
             "is cached and its cover.png is drawn; skills that need nothing, or "
             "have no SKILL.md in the snapshot, are skipped and do not count",
    ),
    concurrency: int | None = typer.Option(
        None, "--concurrency",
        help="Max concurrent LLM calls shared across skills and prompts "
             "(defaults to SKILLS_PROFILES_CONCURRENCY or 2)",
    ),
    prompts_opt: str | None = typer.Option(
        None, "--prompts",
        help="Comma-separated prompt ids to fill in, e.g. 'tagline'. Cached outputs are "
             "reused under the same rules as a full run; use `invalidate` to drop them. "
             "Prompts outside the selection are carried over",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Use a fake LLM, no API calls"),
    debug: bool = typer.Option(
        False, "--debug", help="Dump the rendered system/user prompts to stderr"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable debug logging"
    ),
) -> None:
    """Complete skills: fill missing profiles, then render their missing covers.

    `--limit N` means "make N skills complete": the selection counts a skill
    that is missing any prompt or whose cover.png has not been drawn yet, and
    the run fills both halves for exactly the skills it selected. Rendering is
    paced at `SKILLS_PROFILES_IMAGE_RATE_LIMIT` images/minute per key (default
    2); without an image key the post-pass is skipped with a warning and picked
    up by a later run once the key is set.
    """
    setup_logging(verbose)
    settings = Settings()
    if limit is not None:
        settings.limit = limit
    if concurrency is not None:
        settings.concurrency = concurrency

    prompt_set = load_prompt_set(settings.prompts_dir)
    only = parse_prompt_ids(prompt_set, prompts_opt)

    start = time.monotonic()
    every_skill, skills = served_skills(settings)
    selected = select_skills(settings, prompt_set, skills, only)
    setup_seconds = time.monotonic() - start
    logger.info("Processing %d of %d skills with model=%s%s",
                len(selected), len(skills), settings.model,
                " (dry-run)" if dry_run else "")

    done = 0

    def on_done(_skill, _record, reused: bool) -> None:
        nonlocal done
        done += 1
        if _record.get("failed"):
            detail = "(failed)"
        elif _record.get("skipped"):
            detail = "(skipped: no SKILL.md)"
        elif reused:
            detail = "(cached)"
        else:
            detail = f"{','.join(sorted(_record.get('generated', ())))} " \
                     f"{_record.get('seconds', 0.0):.1f}s"
        logger.info("  [%d/%d] %s: %s", done, len(selected), _skill.id, detail)

    llm = FakeLLM() if dry_run else make_llm(settings)
    stats = RunStats(selected=len(selected))
    generate_start = time.monotonic()
    asyncio.run(
        run_all(llm, settings, selected, prompt_set, on_skill_done=on_done,
                only=only, debug=debug, stats=stats)
    )
    generate_seconds = time.monotonic() - generate_start

    covers_stats = CoverStats()
    covers_seconds = 0.0
    if not dry_run and not settings.image_keys:
        logger.warning("no image endpoint key (SKILLS_PROFILES_IMAGE_API_KEY) - "
                       "covers not rendered; the next run picks them up once the key is set")
    else:
        # `limit` already counted cover-less skills (see select_skills): render
        # exactly the pictures this run's skills are missing, nothing past it
        pending = [s for s in selected if cover_needed(settings, s.id)]
        if pending:
            logger.info("Rendering %d pending cover(s) with model=%s size=%s%s",
                        len(pending), settings.image_model, settings.image_size,
                        " (dry-run)" if dry_run else "")
            images = FakeImages() if dry_run else make_images(settings)
            covers_start = time.monotonic()
            asyncio.run(run_covers(images, settings, pending,
                                   on_skill_done=cover_progress(len(pending)),
                                   stats=covers_stats))
            covers_seconds = time.monotonic() - covers_start
    total_seconds = time.monotonic() - start

    cov = coverage(settings, prompt_set, skills, only)
    avg = stats.llm_seconds / stats.prompts_generated if stats.prompts_generated else 0.0
    logger.info(
        "Done in %.1fs (setup %.1fs, generate %.1fs, covers %.1fs): %d prompt(s) "
        "generated for %d/%d skill(s), %d reused, %d stale cache(s), %d skipped "
        "(no SKILL.md), %d failed; %d cover(s) rendered, %d failed",
        total_seconds, setup_seconds, generate_seconds, covers_seconds,
        stats.prompts_generated, stats.skills_generated, len(selected),
        stats.prompts_reused, stats.prompts_stale, stats.skills_skipped,
        stats.skills_failed, covers_stats.rendered, covers_stats.skills_failed,
    )
    if stats.prompts_generated:
        logger.info("LLM: %d call(s), %.1fs total, %.2fs average per prompt",
                    stats.prompts_generated, stats.llm_seconds, avg)
    # stats.json is the artifact's state, not the run's: how complete it is right
    # now (which snapshot it became, and from which mirror tag, is stamped by the
    # publish step). Run counters and timings stay in the log.
    write_artifact_stats(settings, cov)
    logger.info(
        "Coverage: %d/%d skill(s) complete (%d profiled), %d remaining, %d stale "
        "(upstream changed; see `invalidate --stale`) | cached prompts: %s",
        cov["complete"], cov["skills"], cov["profiled"], cov["remaining"],
        len(stale_result_ids(settings, every_skill)),
        ", ".join(f"{pid} {n}/{cov['skills']}" for pid, n in cov["prompts"].items()),
    )
    # partial failure is not an error: completed prompts are on disk and get
    # published, the rest regenerates on the next run. A total washout (every
    # selected skill failed) is one: it almost always means a systemic problem
    # (bad key, endpoint down) and retrying here would not help.
    if stats.skills_failed:
        logger.warning("%d skill(s) failed - see the errors above", stats.skills_failed)
    if stats.skills_failed and stats.skills_failed == len(selected):
        logger.error("Every selected skill failed - refusing to report success")
        raise typer.Exit(1)


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":
    app()
