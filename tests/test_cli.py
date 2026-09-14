"""End-to-end CLI dry-run test (no network)."""

import json
import re

from typer.testing import CliRunner

from skills_profiles.cli import app

runner = CliRunner()


def test_run_limit_counts_only_skills_that_generate(settings, monkeypatch):
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)

    result = runner.invoke(app, ["run", "--limit", "2", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Processing 2 of 4 skills" in result.output
    assert "(cached)" not in result.output

    # those two are cached now: the budget goes to the next two, not back to them
    result = runner.invoke(app, ["run", "--limit", "2", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Processing 2 of 4 skills" in result.output
    assert "gamma" in result.output
    assert "hotel" in result.output

    # everything is cached: nothing left to do
    result = runner.invoke(app, ["run", "--limit", "2", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Processing 0 of 4 skills" in result.output


def test_run_serves_only_the_top_installed_skills(settings, monkeypatch):
    """`total_limit` is a ceiling on the dataset, not one run: `run --limit 0`
    ("all") still stops at the window, says so, and reports coverage over it.

    The two skills outside a top-2 window stay untouched on disk — the cap is the
    only thing that keeps them from being profiled, since --limit 0 means "every
    skill with gaps".
    """
    settings.total_limit = 2
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    result = runner.invoke(app, ["run", "--limit", "0", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Serving the top 2 of 4 installed skills" in result.output
    assert "Processing 2 of 2 skills" in result.output

    stats = json.loads((settings.output_dir / "stats.json").read_text(encoding="utf-8"))
    assert stats["skills"] == {"total": 2, "profiled": 2, "complete": 2}

    from skills_profiles.outputs import prompt_result_path

    assert prompt_result_path(settings, "owner-c/repo-c/gamma", "domain").exists() is False
    assert prompt_result_path(settings, "owner-h/repo-h/hotel:sub", "domain").exists() is False


def test_run_concurrency_overrides_settings(settings, monkeypatch):
    """`--concurrency` caps LLM parallelism like `--limit` does the budget."""
    settings.concurrency = 8
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)

    result = runner.invoke(app, ["run", "--limit", "1", "--concurrency", "3", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert settings.concurrency == 3


def test_invalidated_prompt_is_regenerated(settings, monkeypatch):
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    runner.invoke(app, ["run", "--limit", "2", "--dry-run"])

    result = runner.invoke(app, ["invalidate", "--prompts", "tagline"])
    assert result.exit_code == 0, result.output
    assert "Invalidated 2 output(s) across 2 skill(s)" in result.output

    result = runner.invoke(app, ["run", "--limit", "2", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "(cached)" not in result.output  # the taglines were regenerated


def test_invalidate_needs_all_to_wipe_everything(settings, monkeypatch):
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    runner.invoke(app, ["run", "--limit", "2", "--dry-run"])

    result = runner.invoke(app, ["invalidate"])
    assert result.exit_code != 0  # no filter, no --all: refuse

    result = runner.invoke(app, ["invalidate", "--all"])
    assert result.exit_code == 0, result.output
    result = runner.invoke(app, ["run", "--limit", "2", "--dry-run"])
    assert "(cached)" not in result.output


def test_run_writes_a_stats_summary(settings, monkeypatch):
    """A run logs a timed summary and overwrites output/stats.json with the
    artifact's current state: complete skills and per-prompt counts."""
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    result = runner.invoke(app, ["run", "--limit", "2", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "Done in" in result.output
    # 2 skills x every prompt in prompts/ (seven text prompts; covers are not one)
    assert "14 prompt(s) generated for 2/2 skill(s)" in result.output
    assert "Coverage:" in result.output
    # progress lines list only the newly generated prompts, with seconds, no markers
    assert "*" not in result.output
    assert re.search(r"owner-a/repo-a/alpha: \S+ \d+\.\d+s", result.output)

    stats = json.loads((settings.output_dir / "stats.json").read_text(encoding="utf-8"))
    assert stats["skills"] == {"total": 4, "profiled": 2, "complete": 2}
    assert all(v == 2 for v in stats["prompts"].values())
    # state only: no run counters, no provenance (that rides beside the data)
    assert set(stats) == {"skills", "prompts", "covers"}
    assert stats["covers"] == {"rendered": 2}, "run renders the personas it just filled in"


def test_run_stats_snapshot_is_overwritten(settings, monkeypatch):
    """stats.json is a single snapshot: the latest run replaces it wholesale.

    The second run's budget moves to the next two skills (the first are cached),
    and the file always describes the whole dataset afterwards.
    """
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    runner.invoke(app, ["run", "--limit", "2", "--dry-run"])
    runner.invoke(app, ["run", "--limit", "2", "--dry-run"])

    stats = json.loads((settings.output_dir / "stats.json").read_text(encoding="utf-8"))
    assert stats["skills"] == {"total": 4, "profiled": 4, "complete": 4}
    assert all(v == 4 for v in stats["prompts"].values())


def test_run_reports_stale_skills(settings, monkeypatch):
    """A run's summary counts skills whose recorded hash no longer matches the
    snapshot; stats.json stays about the artifact, so it carries no stale count."""
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    runner.invoke(app, ["run", "--limit", "0", "--dry-run"])

    # upstream moves: alpha's content changes
    data_file = settings.data_dir / "skills.jsonl"
    entries = [json.loads(line) for line in data_file.read_text(encoding="utf-8").splitlines()]
    for e in entries:
        if e["id"] == "owner-a/repo-a/alpha":
            e["hash"] = "new" + "a" * 61
    data_file.write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
    )

    result = runner.invoke(app, ["run", "--limit", "0", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "1 stale" in result.output

    stats = json.loads((settings.output_dir / "stats.json").read_text(encoding="utf-8"))
    assert stats["skills"]["complete"] == 4  # staleness does not change completeness
    assert "stale" not in stats["skills"]  # a local diagnostic, not artifact state


def test_sync_reports_tag_and_download(settings, monkeypatch):
    """The sync summary names the tag and whether it downloaded."""
    from skills_profiles.data import SyncReport

    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    monkeypatch.setattr(
        "skills_profiles.cli.sync_data",
        lambda s, refresh: SyncReport(
            data_dir=s.data_dir, tag="dist-2026-09-09", downloaded=True, seconds=1.5,
        ),
    )
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0, result.output
    assert "dist-2026-09-09" in result.output
    assert "downloaded" in result.output


def test_invalidate_stale_drops_hash_changed_skills(settings, monkeypatch):
    """`invalidate --stale` drops exactly the skills whose recorded hash no longer
    matches the snapshot (changed or vanished); the next run regenerates them."""
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    runner.invoke(app, ["run", "--limit", "0", "--dry-run"])

    # simulate upstream: alpha's content changed, hotel vanished
    data_file = settings.data_dir / "skills.jsonl"
    entries = [json.loads(line) for line in data_file.read_text(encoding="utf-8").splitlines()]
    for e in entries:
        if e["id"] == "owner-a/repo-a/alpha":
            e["hash"] = "new" + "a" * 61
    entries = [e for e in entries if e["id"] != "owner-h/repo-h/hotel:sub"]
    data_file.write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
    )

    result = runner.invoke(app, ["invalidate", "--stale"])
    assert result.exit_code == 0, result.output
    assert "2 stale skill(s)" in result.output

    # alpha and hotel are gone; beta and gamma are untouched
    from skills_profiles.outputs import load_hashes, prompt_result_path, skill_result_dir

    assert load_hashes(settings) == {
        "owner-b/repo-b/beta": "b" * 64, "owner-c/repo-c/gamma": "c" * 64,
    }
    assert not skill_result_dir(settings, "owner-a/repo-a/alpha").exists()
    assert not skill_result_dir(settings, "owner-h/repo-h/hotel:sub").exists()
    assert prompt_result_path(settings, "owner-b/repo-b/beta", "domain").exists()

    # refill the cache (alpha regenerates with its new hash), then make gamma
    # stale again: --stale --prompts touches only the stale skill's tagline
    runner.invoke(app, ["run", "--limit", "0", "--dry-run"])
    entries = [json.loads(line) for line in data_file.read_text(encoding="utf-8").splitlines()]
    for e in entries:
        if e["id"] == "owner-c/repo-c/gamma":
            e["hash"] = "new" + "c" * 61
    data_file.write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["invalidate", "--stale", "--prompts", "tagline"])
    assert result.exit_code == 0, result.output
    assert prompt_result_path(settings, "owner-c/repo-c/gamma", "tagline").exists() is False
    assert prompt_result_path(settings, "owner-b/repo-b/beta", "tagline").exists()
    assert prompt_result_path(settings, "owner-b/repo-b/beta", "domain").exists()


def test_invalidate_stale_is_a_noop_when_nothing_is_stale(settings, monkeypatch):
    """`--stale` with an up-to-date record invalidates nothing and exits cleanly."""
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    result = runner.invoke(app, ["invalidate", "--stale"])
    assert result.exit_code == 0, result.output
    assert "0 stale skill(s)" in result.output
    assert "Nothing to invalidate" in result.output


def test_invalidate_rejects_unknown_prompt(settings, monkeypatch):
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    result = runner.invoke(app, ["invalidate", "--prompts", "nope"])
    assert result.exit_code != 0
    assert "unknown prompt" in result.output


class FailingForAlpha:
    """LLM that raises for Alpha (matched via its SKILL.md text), delegates the rest."""

    def __init__(self):
        from skills_profiles.llm import FakeLLM

        self.inner = FakeLLM()

    async def create(self, response_model=None, messages=None, **kwargs):
        system = messages[0]["content"] if messages else ""
        if "Alpha does useful things." in system:
            raise RuntimeError("quota exceeded")
        return await self.inner.create(response_model, messages, **kwargs)


class DeadLLM:
    """LLM that fails for every call: a systemic error (bad key, endpoint down)."""

    async def create(self, response_model=None, messages=None, **kwargs):
        raise RuntimeError("endpoint down")


def test_run_survives_partial_skill_failures(settings, monkeypatch):
    """A skill whose generation fails is isolated: the run still exits 0 so CI
    publishes the completed skills; the failure is counted and reported."""
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    monkeypatch.setattr("skills_profiles.cli.make_llm", lambda s: FailingForAlpha())

    result = runner.invoke(app, ["run", "--limit", "0"])
    assert result.exit_code == 0, result.output
    assert "1 failed" in result.output
    assert "owner-a/repo-a/alpha: (failed)" in result.output

    from skills_profiles.outputs import load_hashes, prompt_result_path

    assert set(load_hashes(settings)) == {
        "owner-b/repo-b/beta", "owner-c/repo-c/gamma", "owner-h/repo-h/hotel:sub",
    }
    assert prompt_result_path(settings, "owner-b/repo-b/beta", "domain").exists()


def test_run_exits_nonzero_when_every_skill_fails(settings, monkeypatch):
    """A total washout (every selected skill failed) is a systemic error:
    the run reports it and exits non-zero so CI does not publish."""
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    monkeypatch.setattr("skills_profiles.cli.make_llm", lambda s: DeadLLM())

    result = runner.invoke(app, ["run", "--limit", "0"])
    assert result.exit_code != 0
    assert "4 failed" in result.output
    assert "Every selected skill failed" in result.output
