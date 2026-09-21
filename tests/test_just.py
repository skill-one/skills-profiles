"""End-to-end tests of the justfile, which owns both networked and parallel work.

Everything it is responsible for is verified through it: `just sync` fetching and replacing
the snapshot, `JOBS` bounding the concurrency, an output that already exists never being
rebuilt, and `just invalidate` being the one way an output goes away.

`just` is a command runner rather than a build system, so the skip and the pool are shell
inside the recipe rather than a target graph - which is why these tests exist: nothing else
would pin them. It runs offline: the snapshot comes from a local tarball, and the model
calls are faked with `DRY=1`.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import gen
import index
from conftest import (
    ARCHIVE_ROOT,
    OUTPUT,
    PROJECT_ROOT,
    SCRIPTS,
    SKILLS,
    make_tarball,
    profile_path,
    skill_path,
    write_snapshot,
)

pytestmark = pytest.mark.skipif(shutil.which("just") is None, reason="just is not installed")

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"
GAMMA = "owner-c/repo-c/gamma"
HOTEL = "owner-h/repo-h/hotel:sub"
DOT = "owner-e/.dotcfg/settings"
DELTA = "owner-d/repo-d/delta"
ANGLES = ("blackbox", "comments", "domain", "scenario", "tagline", "whitebox")


@pytest.fixture
def project(tmp_path) -> Path:
    """A throwaway copy of the project: the justfile, the scripts, prompts/ and a fake snapshot,
    so a test can run `just` without touching the real tree.

    The snapshot is written the way `just sync` leaves one, and the catalog is built from it once:
    the window reads the catalog, so a test that wants the mirror's order needs it there.
    """
    project = tmp_path / "project"
    project.mkdir()
    for name in SCRIPTS:
        shutil.copy(PROJECT_ROOT / name, project)
    shutil.copytree(PROJECT_ROOT / "prompts", project / "prompts")
    write_snapshot(project / OUTPUT)
    assert just(project, "index").returncode == 0
    return project


def just(project: Path, *args: str, dry_run: bool = True) -> subprocess.CompletedProcess:
    """Run `just` in `project`, offline by default, with the current interpreter.

    The knobs are command-line overrides, so they lead: `just <knob>=<value> ... <recipe>`.
    SKILLS_PROFILES_* is scrubbed from the environment first, because the justfile's knobs are
    not supposed to come from there - the one thing it does read, `PY`, is set here on purpose.
    """
    environment = {k: v for k, v in os.environ.items() if not k.startswith("SKILLS_PROFILES_")}
    knobs = [f"py={sys.executable}"] + (["dry=1"] if dry_run else [])
    return subprocess.run(["just", *knobs, *args], cwd=project, capture_output=True, text=True,
                          check=False, env=environment)


def outputs(project: Path, skill_id: str) -> Path:
    return profile_path(project / OUTPUT, skill_id)


def json_names(project: Path, skill_id: str) -> list[str]:
    return sorted(p.name for p in outputs(project, skill_id).glob("*.json"))


def counted(text: str, angle: str) -> list[str]:
    """One row of the report's angle table, without its name."""
    return next(line for line in text.splitlines() if line.startswith(f"{angle} ")).split()[1:]


def snapshot(output: Path, skill_id: str) -> Path:
    """The skill's own directory, as published: what a user downloads and installs."""
    return skill_path(output, skill_id)


def resync(project: Path, entries: list[dict]) -> None:
    """Put another snapshot in the tree, and rebuild the catalog that lists it."""
    write_snapshot(project / OUTPUT, entries)
    assert just(project, "index").returncode == 0


# ------------------------------------------------------------------ the batch


def test_just_builds_every_missing_output(project):
    result = just(project, "limit=2", "jobs=4")
    assert result.returncode == 0, result.stderr
    for skill_id in (ALPHA, BETA):
        assert json_names(project, skill_id) == sorted(f"{angle}.json" for angle in ANGLES)
        md_files = sorted(p.name for p in (outputs(project, skill_id) / "md").glob("*.md"))
        assert md_files == sorted(f"{angle}.md" for angle in ANGLES)


def test_just_skips_what_already_exists(project):
    """The window counts work, so a second bounded run takes the next skill instead of redoing this
    one - and every file that is already there is left exactly as it was."""
    assert just(project, "limit=1").returncode == 0
    built = json_names(project, ALPHA)
    stamps = {p.name: p.stat().st_mtime_ns for p in outputs(project, ALPHA).glob("*.json")}

    again = just(project, "limit=1")

    assert again.returncode == 0
    assert ALPHA not in again.stderr
    assert json_names(project, ALPHA) == built
    assert {p.name: p.stat().st_mtime_ns
            for p in outputs(project, ALPHA).glob("*.json")} == stamps
    assert json_names(project, BETA) == sorted(f"{angle}.json" for angle in ANGLES)


def test_the_window_walks_down_the_snapshot(project):
    """`limit` is a count of work, not a position: three one-skill runs build three skills, and the
    next window starts where the last one stopped."""
    for _ in range(2):
        assert just(project, "limit=1").returncode == 0

    assert json_names(project, ALPHA) == sorted(f"{angle}.json" for angle in ANGLES)
    assert json_names(project, BETA) == sorted(f"{angle}.json" for angle in ANGLES)

    assert just(project, "limit=1").returncode == 0

    assert json_names(project, GAMMA) == sorted(f"{angle}.json" for angle in ANGLES)


def test_a_snapshot_that_is_all_built_has_nothing_to_do(project):
    """An empty window is a normal outcome rather than the error it used to be, and it says which
    one it is: every skill already has its angles, and nothing was dispatched."""
    assert just(project, "limit=0").returncode == 0

    again = just(project, "limit=1")

    assert again.returncode == 0
    assert "nothing to build" in again.stderr
    assert "built " not in again.stderr


def test_deleting_an_output_rebuilds_exactly_that_one(project):
    assert just(project, "limit=1", "jobs=4").returncode == 0
    (outputs(project, ALPHA) / "scenario.json").unlink()

    again = just(project, "limit=1", "jobs=4")
    assert again.returncode == 0, again.stderr
    assert again.stderr.count("built ") == 1
    assert "scenario.json" in again.stderr
    assert (outputs(project, ALPHA) / "scenario.json").is_file()
    assert (outputs(project, ALPHA) / "md" / "scenario.md").is_file()


def test_a_call_that_fails_does_not_end_the_run(project, monkeypatch):
    """One unanswered call used to end a batch with hours left in it.

    The run survives it, names the pair it could not do, and keeps building the rest. A
    source the process cannot read stands in for the failure - a dropped TLS handshake
    arrives the same way, as a traceback and a status of 1 - and the two logs are what a
    later run reads to redo exactly the pairs that are missing.
    """
    monkeypatch.setenv("FAIL_LOG", str(project / "failures.txt"))
    monkeypatch.setenv("GEN_ERR_LOG", str(project / "errors.log"))
    (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").chmod(0o000)

    result = just(project, "limit=2", "jobs=4")

    assert result.returncode == 0, result.stderr
    assert json_names(project, ALPHA) == []
    assert json_names(project, BETA) == sorted(f"{angle}.json" for angle in ANGLES)

    failures = (project / "failures.txt").read_text(encoding="utf-8").splitlines()
    assert sorted(failures) == sorted(f"FAILED {angle} {ALPHA}" for angle in ANGLES)
    assert f"failed: {ALPHA} domain" in result.stderr
    assert "Traceback" in (project / "errors.log").read_text(encoding="utf-8")


def test_jobs_is_what_the_pool_gets(project):
    """`jobs` is a pass-through to the pool, so what is worth pinning is that it reaches the
    command line - a run of three generations cannot show how many were in flight."""
    result = subprocess.run(["just", "--dry-run", "jobs=3"], cwd=project,
                            capture_output=True, text=True, check=False, env=os.environ)
    assert result.returncode == 0, result.stderr
    assert "pool=3" in result.stderr
    assert '-P "$pool"' in result.stderr


def test_rpm_paces_the_pool(project):
    """`rpm` turns the pool into a pace: a worker waits `pool * 60 / rpm` between calls, so the
    batch cannot outrun the endpoint however fast the calls come back."""
    result = just(project, "limit=1", "prompt=domain", "rpm=60", "jobs=1")
    assert result.returncode == 0, result.stderr
    assert "pacing: 1 at a time, one call per 1s per worker" in result.stderr


def test_without_rpm_nothing_waits(project):
    result = just(project, "limit=1", "prompt=domain")
    assert result.returncode == 0, result.stderr
    assert "pacing" not in result.stderr


def test_prompt_builds_one_angle_for_every_skill(project):
    """`prompt=<id>` is the column rather than the cell: the angle you just added, for every
    skill in the window, without walking the others."""
    assert just(project, "limit=2", "prompt=domain").returncode == 0
    assert json_names(project, ALPHA) == ["domain.json"]
    assert json_names(project, BETA) == ["domain.json"]


def test_an_unknown_prompt_lists_the_ones_there_are(project):
    result = just(project, "prompt=nosuchangle")
    assert result.returncode != 0
    assert "no prompt 'nosuchangle'" in result.stderr
    assert "domain" in result.stderr


def test_a_repo_whose_name_starts_with_a_dot_is_still_a_skill(project):
    """A shell glob does not match a leading dot, so `skills/*/*/*/SKILL.md` silently drops
    every skill under a repo like `.claude` - which is why the graph is a `find`."""
    assert just(project, "limit=0", "jobs=4").returncode == 0
    assert (outputs(project, DOT) / "domain.json").is_file()


def test_a_bare_just_builds_one_skill(project):
    """The window is one skill by default, so a bare `just` is a smoke run rather than a
    sixty-thousand-job batch; `limit=0` is the whole snapshot, with no cap above it."""
    assert just(project).returncode == 0
    assert json_names(project, ALPHA) == sorted(f"{angle}.json" for angle in ANGLES)
    assert not outputs(project, BETA).exists()


def test_a_bigger_window_reaches_further_down(project):
    """The window is a count of work in the snapshot's own order, so a bigger one only ever adds:
    the second skill's window takes the two after the first window's one."""
    assert just(project, "limit=1").returncode == 0
    assert outputs(project, ALPHA).is_dir()
    assert not outputs(project, BETA).exists()

    assert just(project, "limit=2").returncode == 0

    assert outputs(project, BETA).is_dir()
    assert outputs(project, GAMMA).is_dir()  # the one already built is not counted again
    assert not outputs(project, HOTEL).exists()


def test_limit_zero_is_the_whole_snapshot(project):
    """0 = every skill, including one whose id carries a colon: the directory it lives in
    is the sanitized spelling, and that is what gen.py is handed."""
    assert just(project, "limit=0", "jobs=4").returncode == 0
    assert (outputs(project, HOTEL) / "domain.json").is_file()


def test_the_window_follows_the_snapshots_own_order(project):
    """`limit` counts down the mirror's rows, which upstream writes installs-descending: a bounded
    run does the most installed skills first, not the alphabetically first. This listing leads with
    `delta`, which has no SKILL.md, and the window still fills from the next entry."""
    resync(project, list(reversed(SKILLS)))

    assert just(project, "limit=1", "jobs=4").returncode == 0

    assert outputs(project, DOT).is_dir()
    assert not outputs(project, ALPHA).exists()


def test_a_skill_with_no_source_on_disk_is_not_a_target(project):
    """The mirror lists `delta` but saved no source for it, so its row carries no description. The
    window is filtered by what is on disk, so it is not a target and a batch cannot fail on it
    forever."""
    assert just(project, "limit=0", "jobs=4").returncode == 0
    assert not outputs(project, DELTA).exists()


def test_a_skill_nothing_can_be_read_from_is_not_a_target(project):
    """A header that is not YAML is a skill no prompt can lead with, so the catalog says
    `description: null` and the window skips the row: no call, no file, no failure logged."""
    (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").write_text(
        "---\nname: alpha\ndescription: DEPRECATED: renamed elsewhere\n---\n\nBody.\n",
        encoding="utf-8")
    assert just(project, "index").returncode == 0

    result = just(project, "limit=0", "jobs=4")

    assert result.returncode == 0, result.stderr
    assert not outputs(project, ALPHA).exists()
    assert not (outputs(project, ALPHA) / "domain.json").exists()
    assert json_names(project, BETA) == sorted(f"{angle}.json" for angle in ANGLES)
    assert "failed" not in result.stderr


def test_without_a_catalog_the_window_is_path_order(project):
    """The catalog is the order, not a requirement: with none the listing is the order, which is
    the one order that needs nothing but the tree. The first skill is then the alphabetical one,
    not the entry the catalog would have put first."""
    write_snapshot(project / OUTPUT, list(reversed(SKILLS)))
    (project / OUTPUT / "skills.jsonl").unlink()

    assert just(project, "limit=1", "jobs=4").returncode == 0

    assert outputs(project, ALPHA).is_dir()
    assert not outputs(project, DOT).exists()


def test_a_catalog_whose_ids_do_not_parse_is_no_catalog(project):
    """A catalog that arrives in another shape must not empty the window and silently build
    nothing: it is treated as one that is not there, and the listing carries the run."""
    (project / OUTPUT / "skills.jsonl").write_text(
        "".join(f'{{"installs": 1, "id": "{entry["id"]}"}}\n' for entry in SKILLS),
        encoding="utf-8")

    assert just(project, "limit=1", "jobs=4").returncode == 0

    assert outputs(project, ALPHA).is_dir()


def test_one_output_can_be_built_by_name(project):
    """`just one` builds any single output, including one the current window leaves out,
    and the batch afterwards skips it because it is there."""
    result = just(project, "limit=1", "one", "tagline", GAMMA)
    assert result.returncode == 0, result.stderr
    assert (outputs(project, GAMMA) / "tagline.json").is_file()

    assert just(project, "limit=1").returncode == 0
    assert json_names(project, GAMMA) == ["tagline.json"]


def test_the_documented_dry_switch_works(project):
    """`just DRY=1` is the offline switch a user types, and it has to reach the script as
    the long name - the recipe exports it, and an empty value must stay "not set"."""
    result = just(project, "limit=1", "dry=1", dry_run=False)
    assert result.returncode == 0, result.stderr
    assert (outputs(project, ALPHA) / "domain.json").is_file()


def test_a_dry_run_the_environment_cannot_trigger(project):
    """The knobs are the command line. A `SKILLS_PROFILES_DRY_RUN=1` exported in the shell is
    not read - which is the point: only a run that says `dry=1` is a fake one."""
    result = subprocess.run(
        ["just", f"py={sys.executable}", "one", "domain", ALPHA],
        cwd=project, capture_output=True, text=True, check=False,
        env={**{k: v for k, v in os.environ.items() if not k.startswith("SKILLS_PROFILES_")},
             "SKILLS_PROFILES_DRY_RUN": "1"})
    assert result.returncode != 0
    assert "built " not in result.stderr


def test_invalidate_forgets_exactly_one_prompt(project):
    """Nothing remembers what a file was made from, so this is the invalidation there is -
    and the next run rebuilds that prompt and nothing else."""
    assert just(project, "limit=2", "jobs=4").returncode == 0
    result = just(project, "invalidate", "domain")
    assert result.returncode == 0, result.stderr
    for skill_id in (ALPHA, BETA):
        assert "domain.json" not in json_names(project, skill_id)
        assert not (outputs(project, skill_id) / "md" / "domain.md").exists()
        assert "scenario.json" in json_names(project, skill_id)

    again = just(project, "limit=2", "jobs=4")
    assert again.returncode == 0, again.stderr
    assert again.stderr.count("built ") == 2  # one prompt, two skills
    assert (outputs(project, ALPHA) / "domain.json").is_file()


def test_just_clean_drops_the_profiles_and_keeps_the_sources(project):
    """`clean` is about what was generated: the profiles, the catalog and the report about them. The
    skill directories and the mirror's own files stay - they are what a profile is built from, and
    re-fetching them is the expensive part."""
    assert just(project, "limit=1").returncode == 0
    assert just(project, "index").returncode == 0
    assert outputs(project, ALPHA).is_dir()

    assert just(project, "clean").returncode == 0

    assert not (project / OUTPUT / gen.PROFILES_DIR).exists()
    assert not (project / OUTPUT / "skills.jsonl").exists()
    assert not (project / OUTPUT / index.STATS).exists()
    assert (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").is_file()
    assert (project / OUTPUT / gen.UPSTREAM_DIR / "skills.jsonl").is_file()


def test_just_index_joins_the_mirror_with_the_profiles(project):
    """`just index` writes the catalog: a row per skill the mirror lists, in the mirror's order,
    carrying what was read out of the skill and what was decided about it - and `null` where neither
    has happened. A row keeps the mirror's spelling of the id; its directory is the other one. It
    writes the report beside it from the same walk, so the two cannot describe different trees."""
    assert just(project, "limit=0", "jobs=4").returncode == 0
    (outputs(project, ALPHA) / "domain.json").unlink()

    result = just(project, "index")

    assert result.returncode == 0, result.stderr
    lines = [json.loads(line) for line in
             (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [line["id"] for line in lines] == [
        ALPHA, BETA, GAMMA, HOTEL, DOT, DELTA]
    assert lines[0]["description"].startswith("Tidies a note list")
    assert lines[0]["domain"] is None  # the profile was deleted; the skill is still listed
    assert lines[5]["description"] is None  # no source to read a description from
    text = (project / OUTPUT / index.STATS).read_text(encoding="utf-8")
    assert counted(text, "domain")[:2] == ["4", "5"]  # the deleted json is not progress
    assert counted(text, "comments")[:2] == ["5", "5"]


def test_just_without_a_snapshot_says_what_to_run(tmp_path):
    """A bare `just` before `just sync` must fail with the fix, not a traceback."""
    project = tmp_path / "bare"
    project.mkdir()
    for name in SCRIPTS:
        shutil.copy(PROJECT_ROOT / name, project)
    shutil.copytree(PROJECT_ROOT / "prompts", project / "prompts")

    result = just(project)
    assert result.returncode != 0
    assert "just sync" in result.stderr
    assert "Traceback" not in result.stderr


# ------------------------------------------------------------------- just sync


def test_just_sync_unpacks_the_branch_into_its_two_layers(project, tmp_path):
    """`just sync` is the whole fetch: one tarball, whose skill directories land at the root of the
    tree - complete, because that is what a user installs - and whose other files, its own index
    above all, land beside them."""
    tarball = tmp_path / "snapshot.tar.gz"
    make_tarball(tarball)
    result = just(project, f"snapshot=file://{tarball}", "sync")
    assert result.returncode == 0, result.stderr

    assert (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").is_file()
    # the whole skill directory lands now, not only the SKILL.md
    assert (snapshot(project / OUTPUT, ALPHA) / "extra.md").is_file()
    assert (project / OUTPUT / gen.UPSTREAM_DIR / "skills.jsonl").is_file()
    assert (project / OUTPUT / gen.UPSTREAM_DIR / "repos.jsonl").is_file()
    # and GitHub's <repo>-<branch>/ wrapper is stripped, not nested
    assert not (project / OUTPUT / ARCHIVE_ROOT).exists()


def test_just_sync_rewrites_the_catalog_it_moved_the_sources_under(project, tmp_path):
    """A sync leaves a catalog that names the skills it just fetched, so a run after a bare
    `just sync` is ordered and windowed the same way a run after `just index` is."""
    tarball = tmp_path / "snapshot.tar.gz"
    make_tarball(tarball)
    (project / OUTPUT / "skills.jsonl").unlink()

    assert just(project, f"snapshot=file://{tarball}", "sync").returncode == 0

    lines = (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["id"] for line in lines] == [entry["id"] for entry in SKILLS]


def test_just_sync_replaces_the_snapshot_wholesale(project, tmp_path):
    """A skill that vanished upstream must not keep its files behind."""
    tarball = tmp_path / "snapshot.tar.gz"
    make_tarball(tarball)
    assert just(project, f"snapshot=file://{tarball}", "sync").returncode == 0
    gone = snapshot(project / OUTPUT, ALPHA)
    assert gone.is_dir()

    make_tarball(tarball, [entry for entry in SKILLS if entry["id"] != ALPHA])
    assert just(project, f"snapshot=file://{tarball}", "sync").returncode == 0
    assert not gone.exists()


def test_a_failed_download_leaves_the_previous_snapshot_alone(project):
    """The new tree is unpacked beside the old one, so a broken fetch changes nothing."""
    before = (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").read_bytes()
    result = just(project, "snapshot=file:///nowhere/snapshot.tar.gz", "sync")
    assert result.returncode != 0
    assert (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").read_bytes() == before


def test_just_sync_refuses_a_directory_that_is_not_a_snapshot(tmp_path):
    """`rm -rf` on a configurable path needs a guard in front of it."""
    project = tmp_path / "bare"
    project.mkdir()
    for name in SCRIPTS:
        shutil.copy(PROJECT_ROOT / name, project)
    stray = tmp_path / "stray"
    (stray / "skills" / "junk").mkdir(parents=True)

    result = just(project, f"output_dir={stray}", "sync")
    assert result.returncode != 0
    assert "is not a snapshot" in result.stderr
    assert (stray / "skills" / "junk").is_dir()  # and nothing was deleted


def test_a_snapshot_fetched_by_just_is_what_the_batch_reads(project, tmp_path):
    """The seam between the justfile and the scripts is the tree layout, so the only way
    to test it is to fetch a snapshot and then build from it."""
    shutil.rmtree(project / OUTPUT)
    tarball = tmp_path / "snapshot.tar.gz"
    make_tarball(tarball)
    assert just(project, f"snapshot=file://{tarball}", "sync").returncode == 0
    assert just(project, "limit=1", "jobs=4").returncode == 0
    assert (outputs(project, ALPHA) / "scenario.json").is_file()


def test_just_refresh_retires_only_what_the_new_snapshot_changed(project, tmp_path):
    """`just refresh` is `sync` plus its consequence: the snapshot is replaced, and the profiles
    whose source hash moved with it are dropped so the next batch rebuilds them. A skill the new
    index still holds at the same hash, and one it no longer holds at all, both keep theirs."""
    assert just(project, "limit=0", "jobs=4").returncode == 0
    after = [{**entry, "hash": "f" * 64} if entry["id"] == ALPHA else entry
             for entry in SKILLS if entry["id"] != GAMMA]
    tarball = tmp_path / "snapshot.tar.gz"
    make_tarball(tarball, after)

    result = just(project, f"snapshot=file://{tarball}", "refresh")

    assert result.returncode == 0, result.stderr
    assert not outputs(project, ALPHA).exists()  # upstream changed it
    assert outputs(project, BETA).is_dir()  # untouched upstream
    assert outputs(project, GAMMA).is_dir()  # gone upstream, but already paid for
    assert not (project / ".previous-index").exists()  # the scratch the comparison used is gone
    assert "retired 1 profile(s)" in result.stderr
