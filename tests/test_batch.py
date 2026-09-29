"""The batch driver, tested in-process: the window, the lazy fetch, the pool and sync.

`batch.py` owns the orchestration, so these tests call `batch.main()` directly - no `just`, no
`uv`, no wrapper - and only the three things that *are* the justfile run as `just` subprocesses:
the launcher wiring, the command-line-only dry knob, and the pool flags reaching the command.

Everything runs offline: the listing and the repository tarballs are local `file://` files, and
the endpoints are faked with DRY_RUN. The producers run in-process too, one pool job calling
into the producer module - the stderr/failure-log contract lives at that boundary.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import batch
import index
import readme
from conftest import (
    OUTPUT,
    PROJECT_ROOT,
    SCRIPTS,
    SKILLS,
    make_listing,
    make_repo_tarballs,
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


# --------------------------------------------------------------------------- fixtures


def copy_project(project: Path) -> Path:
    """A throwaway copy of the project: the justfile, the scripts and prompts/, so the in-process
    batch and the `just` launcher checks all run from the copy."""
    project.mkdir(parents=True, exist_ok=True)
    for name in SCRIPTS:
        shutil.copy(PROJECT_ROOT / name, project)
    shutil.copytree(PROJECT_ROOT / "prompts", project / "prompts")
    return project


def isolate(monkeypatch, project: Path, dry: bool = True) -> None:
    """Run from `project` with a scrubbed SKILLS_PROFILES_* environment: the batch gets its paths
    here, and dry is set explicitly rather than leaking from the developer's shell."""
    for key in [k for k in os.environ if k.startswith("SKILLS_PROFILES_")]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(project)
    monkeypatch.setenv("SKILLS_PROFILES_OUTPUT_DIR", "output")
    monkeypatch.setenv("SKILLS_PROFILES_PROMPTS_DIR", str(project / "prompts"))
    if dry:
        monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "1")


def run_batch(monkeypatch, capsys, project: Path, *args: str, dry: bool = True):
    """One in-process batch run; stderr is what the tests assert on, like the old subprocess."""
    isolate(monkeypatch, project, dry)
    rc = batch.main(list(args))
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=rc, stderr=captured.err, stdout=captured.out)


def run_index(monkeypatch, capsys, project: Path):
    rc = index.main([])
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=rc, stderr=captured.err)


def just(project: Path, *args: str, dry_run: bool = True) -> subprocess.CompletedProcess:
    """A real `just` run - only for the launcher tests. The knobs lead, SKILLS_PROFILES_* is
    scrubbed, the current interpreter replaces `uv run python`."""
    environment = {k: v for k, v in os.environ.items() if not k.startswith("SKILLS_PROFILES_")}
    knobs = [f"py={sys.executable}"] + (["dry=1"] if dry_run else [])
    return subprocess.run(["just", *knobs, *args], cwd=project, capture_output=True, text=True,
                          check=False, env=environment)


@pytest.fixture
def project(tmp_path) -> Path:
    """A snapshot already unpacked: every source and repository directory on disk, catalog built."""
    project = copy_project(tmp_path / "project")
    write_snapshot(project / OUTPUT)
    return project


@pytest.fixture
def fresh(tmp_path, monkeypatch) -> Path:
    """A project `sync` has just reconciled with: the catalog lists the rows, no source fetched."""
    project = copy_project(tmp_path / "project")
    listing = make_listing(tmp_path / "listing.jsonl")
    isolate(monkeypatch, project)
    assert batch.main(["sync", "--listing", f"file://{listing}"]) == 0
    return project


def outputs(project: Path, skill_id: str) -> Path:
    return profile_path(project / OUTPUT, skill_id)


def json_names(project: Path, skill_id: str) -> list[str]:
    return sorted(p.name for p in outputs(project, skill_id).glob("*.json"))


def built(project: Path, skill_id: str) -> bool:
    return (outputs(project, skill_id) / "domain.json").is_file()


def snapshot(output: Path, skill_id: str) -> Path:
    """The skill's own directory, as published: what a user downloads and installs."""
    return skill_path(output, skill_id)


def resync(monkeypatch, capsys, project: Path, entries: list[dict]) -> None:
    """Put another snapshot in the tree, and rebuild the catalog that lists it."""
    write_snapshot(project / OUTPUT, entries)
    assert run_index(monkeypatch, capsys, project).returncode == 0


def repos_knob(repos: Path) -> str:
    """The `--repo-tarball` value for an offline fetch: the tarballs `make_repo_tarballs` laid."""
    return f"file://{repos}/{{owner}}_{{repo}}.tgz"


# ------------------------------------------------------------------ the batch


def test_builds_every_missing_output(monkeypatch, capsys, project):
    result = run_batch(monkeypatch, capsys, project,
                       "build", "domain", "--limit", "2", "--jobs", "4")
    assert result.returncode == 0, result.stderr
    for skill_id in (ALPHA, BETA):
        assert json_names(project, skill_id) == ["domain.json"]


def test_skips_what_already_exists(monkeypatch, capsys, project):
    """The window counts work, so a second bounded run takes the next skill instead of redoing
    this one - and the file that is already there is left exactly as it was."""
    assert run_batch(monkeypatch, capsys, project, "build", "domain").returncode == 0
    stamps = {p.name: p.stat().st_mtime_ns for p in outputs(project, ALPHA).glob("*.json")}

    again = run_batch(monkeypatch, capsys, project, "build", "domain")

    assert again.returncode == 0
    assert ALPHA not in again.stderr
    assert {p.name: p.stat().st_mtime_ns
            for p in outputs(project, ALPHA).glob("*.json")} == stamps
    assert json_names(project, BETA) == ["domain.json"]


def test_the_window_walks_down_the_snapshot(monkeypatch, capsys, project):
    """`limit` is a count of work, not a position: three one-skill runs build three skills."""
    for _ in range(2):
        assert run_batch(monkeypatch, capsys, project, "build", "domain").returncode == 0
    assert json_names(project, ALPHA) == ["domain.json"]
    assert json_names(project, BETA) == ["domain.json"]

    assert run_batch(monkeypatch, capsys, project, "build", "domain").returncode == 0

    assert json_names(project, GAMMA) == ["domain.json"]


def test_a_snapshot_that_is_all_built_has_nothing_to_do(monkeypatch, capsys, project):
    """An empty window is a normal outcome rather than the error it used to be."""
    assert run_batch(monkeypatch, capsys, project,
                     "build", "domain", "--limit", "0").returncode == 0

    again = run_batch(monkeypatch, capsys, project, "build", "domain")

    assert again.returncode == 0
    assert "nothing to build" in again.stderr
    assert "built " not in again.stderr


def test_deleting_an_output_rebuilds_exactly_that_one(monkeypatch, capsys, project):
    assert run_batch(monkeypatch, capsys, project,
                     "build", "domain", "--jobs", "4").returncode == 0
    (outputs(project, ALPHA) / "domain.json").unlink()

    again = run_batch(monkeypatch, capsys, project, "build", "domain", "--jobs", "4")
    assert again.returncode == 0, again.stderr
    assert again.stderr.count("built ") == 1
    assert "domain.json" in again.stderr
    assert (outputs(project, ALPHA) / "domain.json").is_file()


def test_a_call_that_fails_does_not_end_the_run(monkeypatch, capsys, project):
    """One unreadable source does not end a batch with hours left in it: the run survives it,
    names the skill it could not do in both logs, and keeps building the rest."""
    isolate(monkeypatch, project)
    monkeypatch.setenv("FAIL_LOG", str(project / "failures.txt"))
    monkeypatch.setenv("GEN_ERR_LOG", str(project / "errors.log"))
    (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").chmod(0o000)

    result = batch.main(["build", "domain", "--limit", "2", "--jobs", "4"])
    err = capsys.readouterr().err

    assert result == 0, err
    assert json_names(project, ALPHA) == []
    assert json_names(project, BETA) == ["domain.json"]
    assert (project / "failures.txt").read_text(encoding="utf-8").splitlines() == [
        f"FAILED domain {ALPHA}"]
    assert f"failed: {ALPHA}" in err
    assert "Traceback" in (project / "errors.log").read_text(encoding="utf-8")


def test_a_batch_where_every_job_fails_is_status_one(monkeypatch, capsys, project):
    """A window whose every producer failed is a broken run, not a green one: partial output is
    published output, so the run survives it - and says so in its exit status."""
    isolate(monkeypatch, project)
    for skill_id in (ALPHA, BETA):
        (snapshot(project / OUTPUT, skill_id) / "SKILL.md").chmod(0o000)

    assert batch.main(["build", "domain", "--limit", "2", "--jobs", "4"]) == 1


def test_build_all_fills_both_angles_in_one_pool(monkeypatch, capsys, project):
    """`all` is the two angles over one shared window: the skills missing either file are built
    for both, so one run leaves each of them whole."""
    result = run_batch(monkeypatch, capsys, project,
                       "build", "all", "--limit", "2", "--jobs", "4")

    assert result.returncode == 0, result.stderr
    for skill_id in (ALPHA, BETA):
        assert json_names(project, skill_id) == ["domain.json"]
        assert (outputs(project, skill_id) / "SKILL.zh.md").is_file()
    assert not built(project, GAMMA)  # the window was two wide
    assert not (outputs(project, GAMMA) / "SKILL.zh.md").exists()


def test_a_repo_whose_name_starts_with_a_dot_is_still_a_skill(monkeypatch, capsys, project):
    result = run_batch(monkeypatch, capsys, project,
                       "build", "domain", "--limit", "0", "--jobs", "4")
    assert result.returncode == 0, result.stderr
    assert (outputs(project, DOT) / "domain.json").is_file()


def test_without_a_limit_the_window_is_one_skill(monkeypatch, capsys, project):
    """The default window is one skill, a smoke run rather than a whole-snapshot batch."""
    result = run_batch(monkeypatch, capsys, project, "build", "domain")
    assert result.returncode == 0, result.stderr
    assert json_names(project, ALPHA) == ["domain.json"]
    assert not built(project, BETA)


def test_a_bigger_window_reaches_further_down(monkeypatch, capsys, project):
    assert run_batch(monkeypatch, capsys, project, "build", "domain").returncode == 0
    assert built(project, ALPHA)
    assert not built(project, BETA)

    assert run_batch(monkeypatch, capsys, project,
                     "build", "domain", "--limit", "2").returncode == 0

    assert built(project, BETA)
    assert built(project, GAMMA)  # the one already built is not counted again
    assert not (outputs(project, HOTEL) / "domain.json").exists()


def test_limit_zero_is_the_whole_snapshot(monkeypatch, capsys, project):
    """0 = every skill, including one whose id carries a colon: the directory takes the sanitized
    spelling, and that is what the producer is handed."""
    result = run_batch(monkeypatch, capsys, project,
                       "build", "domain", "--limit", "0", "--jobs", "4")
    assert result.returncode == 0, result.stderr
    assert (outputs(project, HOTEL) / "domain.json").is_file()


def test_the_window_follows_the_snapshots_own_order(monkeypatch, capsys, project):
    """The batch walks the catalog's rows. This resync leads with `delta`, which is unbuildable,
    and the window fills from the next entry."""
    resync(monkeypatch, capsys, project, list(reversed(SKILLS)))

    result = run_batch(monkeypatch, capsys, project, "build", "domain", "--jobs", "4")

    assert result.returncode == 0, result.stderr
    assert (outputs(project, DOT) / "domain.json").is_file()
    assert not built(project, ALPHA)


def test_a_skill_the_repository_does_not_hold_is_not_built(monkeypatch, capsys, project):
    """The mirror lists `delta` but its repository saved no source for it: the snapshot left it an
    empty directory, so the window leaves it alone."""
    result = run_batch(monkeypatch, capsys, project,
                       "build", "domain", "--limit", "0", "--jobs", "4")
    assert result.returncode == 0, result.stderr
    assert not (outputs(project, DELTA) / "domain.json").exists()


def test_without_a_catalog_the_batch_says_what_to_run(tmp_path, monkeypatch, capsys):
    project = copy_project(tmp_path / "project")
    result = run_batch(monkeypatch, capsys, project, "build", "domain")

    assert result.returncode == 1
    assert "just sync" in result.stderr
    assert "Traceback" not in result.stderr


def test_a_catalog_whose_line_does_not_parse_is_an_error(monkeypatch, capsys, project):
    """A catalog that arrives in another shape must not silently build nothing: the batch says so
    instead of showing a traceback."""
    (project / OUTPUT / "skills.jsonl").write_text(
        '{"id": "owner-a/repo-a/alpha"}\nthis line is not json\n', encoding="utf-8")
    result = run_batch(monkeypatch, capsys, project, "build", "domain", "--jobs", "4")

    assert result.returncode == 1
    assert "not valid JSON" in result.stderr
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------- the lazy fetch


def test_the_batch_fetches_only_the_windows_repositories(fresh, tmp_path, monkeypatch, capsys):
    """A build fetches the repository of the skill it is about to build, and nothing else."""
    repos = make_repo_tarballs(tmp_path / "repos")

    result = run_batch(monkeypatch, capsys, fresh, "build", "domain", "--jobs", "4",
                       "--repo-tarball", repos_knob(repos))

    assert result.returncode == 0, result.stderr
    assert (outputs(fresh, ALPHA) / "domain.json").is_file()
    assert (fresh / OUTPUT / "skills" / "owner-a" / "repo-a").is_dir()  # the repository cache
    assert not (fresh / OUTPUT / "skills" / "owner-b").exists()


def test_a_repository_already_on_disk_is_not_fetched_again(fresh, tmp_path, monkeypatch, capsys):
    """The repository is the cache: once its directory is on disk, a rebuild needs no tarball."""
    repos = make_repo_tarballs(tmp_path / "repos")
    assert run_batch(monkeypatch, capsys, fresh, "build", "domain", "--jobs", "4",
                     "--repo-tarball", repos_knob(repos)).returncode == 0
    assert (outputs(fresh, ALPHA) / "domain.json").is_file()

    shutil.rmtree(tmp_path / "repos")  # the tarballs are gone
    (outputs(fresh, ALPHA) / "domain.json").unlink()

    result = run_batch(monkeypatch, capsys, fresh, "build", "domain", "--jobs", "4",
                       "--repo-tarball", repos_knob(tmp_path / "repos"))

    assert result.returncode == 0, result.stderr
    assert (outputs(fresh, ALPHA) / "domain.json").is_file()  # rebuilt without a download


def test_a_repository_that_fails_to_fetch_fails_only_its_skills(
        fresh, tmp_path, monkeypatch, capsys):
    """One repository that will not download does not end the batch: its skills fail as data,
    a run of nothing but failures is a broken run (exit 1), and the next run, with the tarballs
    in place, builds them."""
    failed = run_batch(monkeypatch, capsys, fresh, "build", "domain", "--limit", "2",
                       "--jobs", "4", "--repo-tarball", repos_knob(tmp_path / "nowhere"))
    assert failed.returncode == 1, failed.stderr
    assert "failed to fetch" in failed.stderr
    assert not (outputs(fresh, ALPHA) / "domain.json").exists()
    assert not (outputs(fresh, BETA) / "domain.json").exists()

    repos = make_repo_tarballs(tmp_path / "repos")
    assert run_batch(monkeypatch, capsys, fresh, "build", "domain", "--limit", "2",
                     "--jobs", "4", "--repo-tarball", repos_knob(repos)).returncode == 0
    assert (outputs(fresh, ALPHA) / "domain.json").is_file()
    assert (outputs(fresh, BETA) / "domain.json").is_file()


def test_a_shared_repository_is_downloaded_once(fresh, tmp_path, monkeypatch, capsys):
    """The fetch is lazy and deduplicated: the first job on a repository unpacks it, every later
    job on the same repository waits on that one download - the tarball count says so."""
    repos = make_repo_tarballs(tmp_path / "repos")
    added = [*SKILLS, {"id": "owner-a/repo-a/newcomer", "installs": "1",
                       "description": "A second skill of the repository alpha came from."}]
    listing = make_listing(tmp_path / "listing.jsonl", added)
    repos = make_repo_tarballs(repos, added)
    assert run_batch(monkeypatch, capsys, fresh, "sync", "--listing", f"file://{listing}",
                     "--repo-tarball", repos_knob(repos)).returncode == 0

    result = run_batch(monkeypatch, capsys, fresh, "build", "domain", "--limit", "0",
                       "--jobs", "8", "--repo-tarball", repos_knob(repos))

    assert result.returncode == 0, result.stderr
    assert "from 6 repository tarball(s)" in result.stderr  # repo-a fetched once for its two skills
    assert (outputs(fresh, ALPHA) / "domain.json").is_file()
    assert (outputs(fresh, "owner-a/repo-a/newcomer") / "domain.json").is_file()


def test_the_repositorys_own_readme_is_not_a_skill(fresh, tmp_path, monkeypatch, capsys):
    """The repository's own root `SKILL.md` is its readme, not a skill; what it ships beside a
    skill's directory is left out too."""
    repos = make_repo_tarballs(tmp_path / "repos")

    assert run_batch(monkeypatch, capsys, fresh, "build", "domain", "--jobs", "4",
                     "--repo-tarball", repos_knob(repos)).returncode == 0

    assert (snapshot(fresh / OUTPUT, ALPHA) / "SKILL.md").is_file()
    assert not (fresh / OUTPUT / "skills" / "owner-a" / "repo-a" / "repo-a-abc1234").exists()
    assert not (snapshot(fresh / OUTPUT, ALPHA) / "extra.md").exists()


def test_a_repository_that_holds_no_skill_is_left_empty(fresh, tmp_path, monkeypatch, capsys):
    """`delta`'s repository holds no `skills/` directory: nothing is unpacked for it, its skill
    directory stays empty, and the window leaves it alone."""
    repos = make_repo_tarballs(tmp_path / "repos")

    assert run_batch(monkeypatch, capsys, fresh, "build", "domain", "--limit", "0",
                     "--jobs", "4", "--repo-tarball", repos_knob(repos)).returncode == 0

    assert (fresh / OUTPUT / "skills" / "owner-d" / "repo-d").is_dir()  # on disk either way
    assert not (outputs(fresh, DELTA) / "SKILL.md").exists()
    assert not (outputs(fresh, DELTA) / "domain.json").exists()


# ---------------------------------------------------------------- sync


def _sync(monkeypatch, capsys, project: Path, listing: Path, repos: Path | None = None):
    args = ["sync", "--listing", f"file://{listing}"]
    if repos is not None:
        args += ["--repo-tarball", repos_knob(repos)]
    return run_batch(monkeypatch, capsys, project, *args)


def test_sync_pulls_the_listing_into_the_catalog(tmp_path, monkeypatch, capsys):
    """Sync writes one catalog row per listed skill, its joined fields null until fetched."""
    project = copy_project(tmp_path / "project")
    listing = make_listing(tmp_path / "listing.jsonl")

    assert _sync(monkeypatch, capsys, project, listing).returncode == 0

    lines = [json.loads(line) for line in
             (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [line["id"] for line in lines] == [entry["id"] for entry in SKILLS]
    assert all(line["description"] is None for line in lines)
    assert not (project / OUTPUT / "skills").exists()  # sync fetches no source on its own


def test_sync_keeps_the_sources_it_already_has(project, tmp_path, monkeypatch, capsys):
    """Sync moves the listing, not the sources: the tree's sources and their filled fields stay
    exactly as they were."""
    before = (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").read_bytes()
    listing = make_listing(tmp_path / "listing.jsonl", list(reversed(SKILLS)))

    assert _sync(monkeypatch, capsys, project, listing).returncode == 0

    lines = [json.loads(line) for line in
             (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [line["id"] for line in lines] == [entry["id"] for entry in reversed(SKILLS)]
    alpha = next(line for line in lines if line["id"] == ALPHA)
    assert alpha["description"].startswith("Tidies a note list")
    assert (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").read_bytes() == before


def test_sync_refetches_the_repository_a_new_skill_was_added_to(
        project, tmp_path, monkeypatch, capsys):
    """A listing that adds a skill to a repository already on disk refetches it and merges the new
    source in; what was already built is left alone and the repository directory is not dropped."""
    assert run_batch(monkeypatch, capsys, project, "build", "domain", "--jobs", "4").returncode == 0
    assert (outputs(project, ALPHA) / "domain.json").is_file()
    added = [*SKILLS, {"id": "owner-a/repo-a/newcomer", "installs": "1",
                       "description": "A skill the listing added later."}]
    listing = make_listing(tmp_path / "listing.jsonl", added)
    repos = make_repo_tarballs(tmp_path / "repos", added)

    assert _sync(monkeypatch, capsys, project, listing, repos).returncode == 0

    assert (outputs(project, ALPHA) / "domain.json").is_file()  # not rebuilt
    assert (snapshot(project / OUTPUT, "owner-a/repo-a/newcomer") / "SKILL.md").is_file()
    assert (project / OUTPUT / "skills" / "owner-b" / "repo-b").is_dir()  # untouched
    lines = [json.loads(line) for line in
             (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()]
    assert "owner-a/repo-a/newcomer" in [line["id"] for line in lines]


def test_a_failed_sync_leaves_the_catalog_alone(project, tmp_path, monkeypatch, capsys):
    """The listing failing to download aborts before the catalog is rewritten."""
    before = (project / OUTPUT / "skills.jsonl").read_bytes()

    result = run_batch(monkeypatch, capsys, project, "sync",
                       "--listing", "file:///nowhere/listing.jsonl")

    assert result.returncode == 1
    assert (project / OUTPUT / "skills.jsonl").read_bytes() == before


def test_sync_names_the_skills_the_mirror_dropped(project, tmp_path, monkeypatch, capsys):
    """A skill the mirror no longer lists stays in the tree, and sync says so rather than
    dropping it silently: its files are a decision to make, not a surprise to find."""
    listing = make_listing(tmp_path / "listing.jsonl", SKILLS[1:])

    result = _sync(monkeypatch, capsys, project, listing)

    assert result.returncode == 0, result.stderr
    assert f"the mirror dropped {ALPHA}" in result.stderr
    assert (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").is_file()
    lines = [json.loads(line) for line in
             (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()]
    assert ALPHA not in [line["id"] for line in lines]


# ------------------------------------------------------ the zh page angle


def test_the_skill_zh_batch_writes_the_chinese_pages(monkeypatch, capsys, project):
    """The skill_zh window fills with SKILL.zh.md carrying the machine-assembled dry-run page."""
    assert run_batch(monkeypatch, capsys, project, "build", "skill_zh", "--limit", "2",
                     "--jobs", "4").returncode == 0
    for skill_id in (ALPHA, BETA):
        text = (outputs(project, skill_id) / "SKILL.zh.md").read_text(encoding="utf-8")
        assert text.startswith("---\n")  # the assembled front matter
        assert "description: 【占位】" in text
        assert "【占位】" in text.split("---\n\n", 1)[1]
    assert not (outputs(project, GAMMA) / "SKILL.zh.md").exists()  # the window was two wide

    for page in project.glob(f"{OUTPUT}/skills/**/SKILL.zh.md"):  # invalidation is deletion
        page.unlink()
    for skill_id in (ALPHA, BETA):
        assert not (outputs(project, skill_id) / "SKILL.zh.md").exists()


def test_the_zh_page_carries_the_chinese_into_the_catalog(monkeypatch, capsys, project):
    """`index` reads the description out of each zh page's front matter into the catalog rows,
    null where the page is not built yet."""
    assert run_batch(monkeypatch, capsys, project, "build", "skill_zh", "--limit", "0",
                     "--jobs", "4").returncode == 0
    assert run_index(monkeypatch, capsys, project).returncode == 0

    lines = [json.loads(line) for line in
             (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [line["id"] for line in lines] == [ALPHA, BETA, GAMMA, HOTEL, DOT, DELTA]
    assert lines[0]["description_zh"].startswith("【占位】")
    assert lines[0]["description_zh"].endswith("the whole pile searchable.")
    assert lines[0]["domain"] is None  # only the zh page was built


def test_deletion_is_the_invalidation(monkeypatch, capsys, project):
    """Deleting an angle file is the whole invalidation: the next run rebuilds exactly it."""
    assert run_batch(monkeypatch, capsys, project, "build", "domain", "--limit", "2",
                     "--jobs", "4").returncode == 0
    for label in project.glob(f"{OUTPUT}/skills/**/domain.json"):
        label.unlink()

    again = run_batch(monkeypatch, capsys, project, "build", "domain", "--limit", "2",
                      "--jobs", "4")
    assert again.returncode == 0, again.stderr
    assert again.stderr.count("built ") == 2
    assert (outputs(project, ALPHA) / "domain.json").is_file()


def test_index_joins_the_mirror_with_the_profiles(monkeypatch, capsys, project):
    """The catalog has a row per listed skill in order; deleting one label makes that field null,
    and the README written from the same walk says so."""
    assert run_batch(monkeypatch, capsys, project, "build", "domain", "--limit", "0",
                     "--jobs", "4").returncode == 0
    (outputs(project, ALPHA) / "domain.json").unlink()
    assert run_index(monkeypatch, capsys, project).returncode == 0

    lines = [json.loads(line) for line in
             (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [line["id"] for line in lines] == [ALPHA, BETA, GAMMA, HOTEL, DOT, DELTA]
    assert lines[0]["description"].startswith("Tidies a note list")
    assert lines[0]["domain"] is None
    text = (project / OUTPUT / readme.README).read_text(encoding="utf-8")
    assert "- **domain**: 4 of 6 labelled (66.7%)" in text


# ----------------------------------------------------- the justfile itself


def test_just_launches_the_batch(project):
    """The one end-to-end launcher check: a bare `just` reaches `batch.py build domain` and the
    dry-run page lands through the real recipes."""
    result = just(project)
    assert result.returncode == 0, result.stderr
    assert (outputs(project, ALPHA) / "domain.json").is_file()
    assert not built(project, BETA)


def test_a_dry_run_the_environment_cannot_trigger(project):
    """The knobs are the command line. A SKILLS_PROFILES_DRY_RUN exported in the shell is not read:
    the default recipe exports the knob empty, so the run is a real one - with no key the skill
    fails and nothing is written, rather than a dry-run output landing."""
    result = subprocess.run(
        ["just", f"py={sys.executable}"],
        cwd=project, capture_output=True, text=True, check=False,
        env={**{k: v for k, v in os.environ.items() if not k.startswith("SKILLS_PROFILES_")},
             "SKILLS_PROFILES_DRY_RUN": "1"})
    assert not (outputs(project, ALPHA) / "domain.json").is_file()
    assert f"failed: {ALPHA}" in result.stderr


def test_the_build_and_clean_recipes_reach_the_driver(project):
    """The two inverse recipes pass the angle and the window knobs through verbatim - dry, so
    nothing runs or is deleted."""
    cases = {
        ("build", "domain"): "batch.py build domain --limit 1 --jobs 32",
        ("build", "skill_zh"): "batch.py build skill_zh --limit 1 --jobs 32",
        ("build", "all"): "batch.py build all --limit 1 --jobs 32",
        ("clean", "domain"): "batch.py clean domain --limit 1",
        ("clean", "skill_zh"): "batch.py clean skill_zh --limit 1",
        ("clean", "all"): "batch.py clean all --limit 1",
    }
    for args, expected in cases.items():
        result = subprocess.run(["just", "--dry-run", *args], cwd=project,
                                capture_output=True, text=True, check=False, env=os.environ)
        assert result.returncode == 0, result.stderr
        assert expected in result.stderr


def test_clean_is_the_inverse_window_of_build(monkeypatch, capsys, project):
    """Build windows the first N skills MISSING the file; clean windows the first N that HAVE it,
    same catalog order. With a default limit of one, clean forgets only the first built skill,
    and the next build regenerates exactly it."""
    assert run_batch(monkeypatch, capsys, project, "build", "domain", "--limit", "0",
                     "--jobs", "4").returncode == 0
    assert (outputs(project, ALPHA) / "domain.json").is_file()
    assert (outputs(project, BETA) / "domain.json").is_file()

    assert run_batch(monkeypatch, capsys, project, "clean", "domain").returncode == 0
    assert not (outputs(project, ALPHA) / "domain.json").exists()  # the first built one
    assert (outputs(project, BETA) / "domain.json").is_file()      # nothing else touched

    # the rebuild walks the same order: alpha is the one missing file, and it comes back
    assert run_batch(monkeypatch, capsys, project, "build", "domain", "--jobs", "4"
                     ).returncode == 0
    assert (outputs(project, ALPHA) / "domain.json").is_file()


def test_clean_takes_only_its_own_angle(monkeypatch, capsys, project):
    """Cleaning one angle leaves the other angle's file riding along."""
    assert run_batch(monkeypatch, capsys, project, "build", "domain", "--limit", "0",
                     "--jobs", "4").returncode == 0
    assert run_batch(monkeypatch, capsys, project, "build", "skill_zh", "--limit", "0",
                     "--jobs", "4").returncode == 0

    assert run_batch(monkeypatch, capsys, project, "clean", "domain", "--limit", "0"
                     ).returncode == 0
    assert not (outputs(project, ALPHA) / "domain.json").exists()
    assert (outputs(project, ALPHA) / "SKILL.zh.md").is_file()


def test_clean_all_limit_zero_then_sync_is_the_full_reset(
        monkeypatch, capsys, project, tmp_path):
    """`clean all` with no cap forgets every model output; sync then rewrites the catalog and the
    READMEs. End state: angles gone, sources kept, catalog fresh."""
    assert run_batch(monkeypatch, capsys, project, "clean", "all", "--limit", "0"
                     ).returncode == 0

    assert not (outputs(project, ALPHA) / "domain.json").exists()
    assert not (outputs(project, ALPHA) / "SKILL.zh.md").exists()
    assert (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").is_file()  # the sources survive
    assert _sync(monkeypatch, capsys, project, make_listing(tmp_path / "listing.jsonl")
                 ).returncode == 0
    lines = [json.loads(line) for line in
             (project / OUTPUT / "skills.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [line["id"] for line in lines] == [entry["id"] for entry in SKILLS]
    assert (project / OUTPUT / readme.README).is_file()
    assert (project / OUTPUT / readme.README_ZH).is_file()


def test_clean_with_nothing_built_is_a_message(monkeypatch, capsys, project):
    """An inverse window over an unbuilt tree removes nothing and says so, exit 0."""
    result = run_batch(monkeypatch, capsys, project, "clean", "domain", "--limit", "0")
    assert result.returncode == 0
    assert "nothing to clean" in result.stderr


def test_a_bad_angle_is_argparse_s_to_reject(project):
    """The angle is passed through verbatim, so a bad one never deletes a thing: the driver's
    argparse stops the run with the choices spelled out."""
    result = subprocess.run(["just", f"py={sys.executable}", "clean", "bogus"], cwd=project,
                            capture_output=True, text=True, check=False,
                            env={k: v for k, v in os.environ.items()
                                 if not k.startswith("SKILLS_PROFILES_")})
    assert result.returncode != 0
    assert "invalid choice: 'bogus' (choose from domain, skill_zh, all)" in result.stderr
    assert (snapshot(project / OUTPUT, ALPHA) / "SKILL.md").is_file()  # nothing was touched


def test_just_passes_the_pool_flags(project):
    """`jobs` and `fetch_jobs` reach `batch.py` verbatim - the justfile is only a launcher."""
    result = subprocess.run(["just", "--dry-run", "jobs=3", "fetch_jobs=9"], cwd=project,
                            capture_output=True, text=True, check=False, env=os.environ)
    assert result.returncode == 0, result.stderr
    assert "--jobs 3" in result.stderr
    assert "--fetch-jobs 9" in result.stderr
