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
from conftest import (
    ARCHIVE_ROOT,
    DATA_ROOT,
    PROJECT_ROOT,
    SCRIPTS,
    SKILLS,
    make_tarball,
    skill_path,
    write_dataset,
)

pytestmark = pytest.mark.skipif(shutil.which("just") is None, reason="just is not installed")

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"
GAMMA = "owner-c/repo-c/gamma"
ANGLES = ("blackbox", "comments", "domain", "scenario", "tagline", "whitebox")


@pytest.fixture
def project(tmp_path) -> Path:
    """A throwaway copy of the project: the justfile, the script, prompts/ and a fake
    snapshot, so a test can run `just` without touching the real tree."""
    project = tmp_path / "project"
    project.mkdir()
    for name in SCRIPTS:
        shutil.copy(PROJECT_ROOT / name, project)
    shutil.copytree(PROJECT_ROOT / "prompts", project / "prompts")
    write_dataset(project / DATA_ROOT)
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
    return project / "output" / "skills" / gen.skill_dir_name(skill_id)


def json_names(project: Path, skill_id: str) -> list[str]:
    return sorted(p.name for p in outputs(project, skill_id).glob("*.json"))


# ------------------------------------------------------------------ the batch


def test_just_builds_every_missing_output(project):
    result = just(project, "limit=2", "jobs=4")
    assert result.returncode == 0, result.stderr
    for skill_id in (ALPHA, BETA):
        assert json_names(project, skill_id) == sorted(f"{angle}.json" for angle in ANGLES)
        md_files = sorted(p.name for p in (outputs(project, skill_id) / "md").glob("*.md"))
        assert md_files == sorted(f"{angle}.md" for angle in ANGLES)


def test_just_skips_what_already_exists(project):
    assert just(project, "limit=1").returncode == 0
    built = json_names(project, ALPHA)
    stamps = {p.name: p.stat().st_mtime_ns for p in outputs(project, ALPHA).glob("*.json")}

    again = just(project, "limit=1")
    assert again.returncode == 0
    assert "built " not in again.stderr
    assert json_names(project, ALPHA) == built
    assert {p.name: p.stat().st_mtime_ns
            for p in outputs(project, ALPHA).glob("*.json")} == stamps


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
    (skill_path(project / DATA_ROOT, ALPHA) / "SKILL.md").chmod(0o000)

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
    assert (outputs(project, "owner-e/.dotcfg/settings") / "domain.json").is_file()


def test_a_bare_just_builds_one_skill(project):
    """The window is one skill by default, so a bare `just` is a smoke run rather than a
    sixty-thousand-job batch; `limit=0` is the whole snapshot, with no cap above it."""
    assert just(project).returncode == 0
    assert json_names(project, ALPHA) == sorted(f"{angle}.json" for angle in ANGLES)
    assert not outputs(project, BETA).exists()


def test_limit_windows_the_skills_and_keeps_what_is_already_built(project):
    """LIMIT is a window over the snapshot in path order.

    The build graph is read off the directory listing, so there are no install counts left
    to rank by; what the window is *for* is unchanged - a bounded batch, and a bigger
    window only ever adds work.
    """
    assert just(project, "limit=1").returncode == 0
    assert outputs(project, ALPHA).is_dir()
    assert not outputs(project, BETA).exists()

    # raising the window brings the next skill in; what is already built stays
    assert just(project, "limit=2").returncode == 0
    assert outputs(project, BETA).is_dir()


def test_limit_zero_is_the_whole_snapshot(project):
    """0 = every skill, including one whose id carries a colon: the directory it lives in
    is the sanitized spelling, and that is what gen.py is handed."""
    assert just(project, "limit=0", "jobs=4").returncode == 0
    assert (outputs(project, "owner-h/repo-h/hotel:sub") / "domain.json").is_file()


def test_the_window_follows_the_snapshots_own_order(project):
    """`limit` counts down the snapshot's index, which upstream writes installs-descending: a
    bounded run does the most installed skills first, not the alphabetically first. This index
    leads with `delta`, which has no SKILL.md, and the window still fills from the next entry."""
    write_dataset(project / DATA_ROOT, list(reversed(SKILLS)))

    assert just(project, "limit=1", "jobs=4").returncode == 0

    assert outputs(project, "owner-e/.dotcfg/settings").is_dir()
    assert not outputs(project, ALPHA).exists()


def test_a_skill_with_no_source_on_disk_is_not_a_target(project):
    """The index names `delta` but upstream saved no SKILL.md for it. The window is filtered by
    what is on disk, so it is not a target and a batch cannot fail on it forever."""
    assert just(project, "limit=0", "jobs=4").returncode == 0
    assert not outputs(project, "owner-d/repo-d/delta").exists()


def test_without_an_index_the_window_is_path_order(project):
    """The index is the order, not a requirement: with none the listing is the order, which is
    the one order that needs nothing but the tree. The first skill is then the alphabetical one,
    not the entry the index would have put first."""
    write_dataset(project / DATA_ROOT, list(reversed(SKILLS)))
    (project / DATA_ROOT / "skills.jsonl").unlink()

    assert just(project, "limit=1", "jobs=4").returncode == 0

    assert outputs(project, ALPHA).is_dir()
    assert not outputs(project, "owner-e/.dotcfg/settings").exists()


def test_an_index_whose_ids_do_not_parse_is_no_index(project):
    """An index that arrives in another shape must not empty the window and silently build
    nothing: it is treated as one that is not there, and the listing carries the run."""
    (project / DATA_ROOT / "skills.jsonl").write_text(
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


def test_just_clean_drops_the_profiles_and_keeps_the_snapshot(project):
    """`clean` is about the generated profiles. The snapshot sits in the same root so that the
    whole of it can be published as one directory, but re-fetching it is still the expensive
    part - so it survives."""
    assert just(project, "limit=1").returncode == 0
    assert just(project, "index").returncode == 0
    assert (project / "output" / "skills").is_dir()

    assert just(project, "clean").returncode == 0

    assert not (project / "output" / "skills").exists()
    assert not (project / "output" / "skills.jsonl").exists()
    assert (project / DATA_ROOT / "skills.jsonl").is_file()


def test_just_index_is_the_tree_in_one_file(project):
    """`just index` flattens the domain over the skills it finds: in path order, with the colon
    in an id spelled the way its directory spells it, and with a skill whose domain was deleted
    left out rather than written as an empty row."""
    assert just(project, "limit=0", "jobs=4").returncode == 0
    (outputs(project, ALPHA) / "domain.json").unlink()

    result = just(project, "index")

    assert result.returncode == 0, result.stderr
    path = project / "output" / "skills.jsonl"
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [line["id"] for line in lines] == [
        BETA, GAMMA, "owner-e/.dotcfg/settings", "owner-h/repo-h/hotel_sub"]
    assert lines[0] == {"id": BETA, "domain": "开发编程", "reason": "离线演示占位内容"}


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


def test_just_sync_unpacks_the_branch(project, tmp_path):
    """`just sync` is the whole fetch: one tarball, unpacked into the data dir."""
    tarball = tmp_path / "snapshot.tar.gz"
    make_tarball(tarball)
    result = just(project, f"snapshot=file://{tarball}", "sync")
    assert result.returncode == 0, result.stderr

    data_dir = project / DATA_ROOT
    assert (skill_path(data_dir, ALPHA) / "SKILL.md").is_file()
    # the whole branch lands now, not only the index and the SKILL.md files
    assert (skill_path(data_dir, ALPHA) / "extra.md").is_file()
    # and GitHub's <repo>-<branch>/ wrapper is stripped, not nested
    assert not (data_dir / ARCHIVE_ROOT).exists()


def test_just_sync_replaces_the_snapshot_wholesale(project, tmp_path):
    """A skill that vanished upstream must not keep its files behind."""
    tarball = tmp_path / "snapshot.tar.gz"
    make_tarball(tarball)
    assert just(project, f"snapshot=file://{tarball}", "sync").returncode == 0
    gone = skill_path(project / DATA_ROOT, ALPHA)
    assert gone.is_dir()

    make_tarball(tarball, [entry for entry in SKILLS if entry["id"] != ALPHA])
    assert just(project, f"snapshot=file://{tarball}", "sync").returncode == 0
    assert not gone.exists()


def test_a_failed_download_leaves_the_previous_snapshot_alone(project):
    """The new tree is unpacked beside the old one, so a broken fetch changes nothing."""
    before = (skill_path(project / DATA_ROOT, ALPHA) / "SKILL.md").read_bytes()
    result = just(project, "snapshot=file:///nowhere/snapshot.tar.gz", "sync")
    assert result.returncode != 0
    assert (skill_path(project / DATA_ROOT, ALPHA) / "SKILL.md").read_bytes() == before


def test_just_sync_refuses_a_directory_that_is_not_a_snapshot(tmp_path):
    """`rm -rf` on a configurable path needs a guard in front of it."""
    project = tmp_path / "bare"
    project.mkdir()
    for name in SCRIPTS:
        shutil.copy(PROJECT_ROOT / name, project)
    stray = tmp_path / "stray"
    (stray / "junk").mkdir(parents=True)

    result = just(project, f"data_dir={stray}", "sync")
    assert result.returncode != 0
    assert "is not a snapshot" in result.stderr
    assert (stray / "junk").is_dir()  # and nothing was deleted


def test_a_snapshot_fetched_by_just_is_what_the_batch_reads(project, tmp_path):
    """The seam between the justfile and the script is the data dir layout, so the only way
    to test it is to fetch a snapshot and then build from it."""
    shutil.rmtree(project / DATA_ROOT)
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
    assert not (project / ".snapshot-index").exists()  # the scratch the comparison used is gone
    assert "retired 1 skill(s)" in result.stderr
