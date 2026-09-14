"""The publish step's stats.json stamping (see stamp-stats.sh).

The pipeline writes stats.json as pure artifact state; the publish step adds the
provenance it alone knows — `publishedAt` and the `upstream` mirror tag. What
this covers is the property the publish decision rests on: stripping the stamp is
lossless and stable, so "did anything really change" can be answered without
being fooled by a snapshot that only differs in when it was published.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / ".github/actions/publish-dist/stamp-stats.sh"

ARTIFACT_STATE = {
    "covers": {"rendered": 999},
    "prompts": {"persona": 1000, "domain": 1000},
    "skills": {"complete": 999, "profiled": 1000, "total": 1000},
}

pytestmark = pytest.mark.skipif(shutil.which("jq") is None, reason="needs jq")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, check=False)


def write_stats(path: Path, stats: dict) -> Path:
    path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def read_stats(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def stats(tmp_path: Path) -> Path:
    return write_stats(tmp_path / "stats.json", ARTIFACT_STATE)


def test_stamp_adds_both_fields_without_touching_the_artifact_state(stats: Path):
    assert run("stamp", str(stats), "2026-09-13T01:02:03Z", "dist-2026-09-09").returncode == 0
    assert read_stats(stats) == {
        **ARTIFACT_STATE,
        "publishedAt": "2026-09-13T01:02:03Z",
        "upstream": "dist-2026-09-09",
    }


def test_stamp_keeps_the_layout_the_pipeline_writes(stats: Path):
    """Two-space indent, sorted keys, trailing newline: a stamped file must not
    look like a different artifact than the one `run` wrote."""
    run("stamp", str(stats), "2026-09-13T01:02:03Z", "dist-2026-09-09")
    text = stats.read_text(encoding="utf-8")
    assert text == json.dumps(read_stats(stats), indent=2, sort_keys=True) + "\n"


def test_stamp_without_a_dataset_carries_no_upstream_field(stats: Path):
    """A snapshot publishing profiles only must not claim a mirror it lacks —
    and must not write `null` or `""` either, which a consumer would read as a
    ref it can join on."""
    run("stamp", str(stats), "2026-09-13T01:02:03Z", "")
    assert read_stats(stats) == {**ARTIFACT_STATE, "publishedAt": "2026-09-13T01:02:03Z"}
    assert "upstream" not in read_stats(stats)


def test_restamping_replaces_the_previous_values(stats: Path):
    """The next publish overwrites both fields rather than accumulating keys, so
    a snapshot always describes itself."""
    run("stamp", str(stats), "2026-09-13T01:02:03Z", "dist-2026-09-09")
    run("stamp", str(stats), "2026-09-14T08:00:00Z", "dist-2026-09-12")
    stamped = read_stats(stats)
    assert stamped["publishedAt"] == "2026-09-14T08:00:00Z"
    assert stamped["upstream"] == "dist-2026-09-12"
    assert list(stamped).count("publishedAt") == 1


def test_core_is_the_same_whether_or_not_the_file_is_stamped(stats: Path):
    """The invariant `publish-dist` judges a no-op run by: a re-published
    snapshot whose only difference is its stamp must compare equal to itself with
    the stamp off, so a day's sync that changed nothing publishes nothing."""
    unstamped = run("core", str(stats)).stdout
    run("stamp", str(stats), "2026-09-13T01:02:03Z", "dist-2026-09-09")
    assert run("core", str(stats)).stdout == unstamped


def test_core_reads_a_snapshot_off_stdin(tmp_path: Path):
    """What actually got published is read back with `git show … | core -`, so
    the comparison must work on a stream, not only on a file."""
    snapshot = write_stats(tmp_path / "snapshot.json",
                           {**ARTIFACT_STATE, "publishedAt": "x", "upstream": "y"})
    with snapshot.open(encoding="utf-8") as handle:
        proc = subprocess.run(["bash", str(SCRIPT), "core", "-"], stdin=handle,
                              capture_output=True, text=True, check=True)
    assert json.loads(proc.stdout) == ARTIFACT_STATE


def test_stamp_refuses_to_invent_a_stats_file(tmp_path: Path):
    """A run with no stats.json has nothing to describe; silently creating one
    would publish counts no pipeline ever computed."""
    proc = run("stamp", str(tmp_path / "missing.json"), "2026-09-13T01:02:03Z", "")
    assert proc.returncode != 0
    assert not (tmp_path / "missing.json").exists()


def test_unknown_subcommand_is_a_usage_error():
    proc = run("publish", "stats.json")
    assert proc.returncode == 2
    assert "usage" in proc.stderr
