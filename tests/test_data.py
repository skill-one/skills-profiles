"""Tests for skills.jsonl parsing, snapshot sync and local SKILL.md reads."""

import json
from pathlib import Path

import httpx
import pytest
from conftest import fake_download, make_tarball, skill_md_text

import skills_profiles.data as data_mod
from skills_profiles.config import DIST_BRANCH, LATEST_URL, TARBALL_URL, Settings, tarball_url
from skills_profiles.data import (
    latest_dist_tag,
    load_skills,
    read_marker,
    read_skill_md,
    skill_md_path,
    stale_result_ids,
    sync_data,
)
from skills_profiles.outputs import load_hashes, write_index


def test_loads_only_valid_skills_sorted_by_installs(settings):
    skills = load_skills(settings)
    assert [s.id for s in skills] == [
        "owner-a/repo-a/alpha", "owner-b/repo-b/beta",
        "owner-c/repo-c/gamma", "owner-h/repo-h/hotel:sub",
    ]
    assert skills[0].installs == 300


def test_skill_md_empty_until_read(settings):
    """Loading the index alone reads no SKILL.md: the source comes on demand."""
    skills = load_skills(settings)
    assert skills[0].skill_md == ""
    assert "Alpha does useful things" in read_skill_md(settings, skills[0])


def test_prose_fields_in_the_index_are_ignored(settings):
    """Only what a run acts on is kept: the index's name/description/source are
    in the mirror's data but never reach a prompt, which reads SKILL.md instead."""
    skill = load_skills(settings)[0]
    assert set(skill.model_dump()) == {"id", "installs", "hash", "skill_md"}


def test_colon_slug_read_from_underscore_directory(settings):
    hotel = next(s for s in load_skills(settings) if s.id == "owner-h/repo-h/hotel:sub")
    assert "Hotel does useful things" in read_skill_md(settings, hotel)


def test_skill_md_lives_at_the_snapshot_path(settings):
    skill = load_skills(settings)[0]
    expected = Path("skills") / skill.id.replace(":", "_") / "SKILL.md"
    assert skill_md_path(settings, skill).relative_to(settings.data_dir) == expected
    assert skill_md_path(settings, skill).read_text(
        encoding="utf-8"
    ) == skill_md_text({"id": skill.id, "name": "Alpha", "hash": skill.hash})


def test_skill_md_missing_in_snapshot_returns_none(settings):
    """A skill the snapshot has no source for yields nothing."""
    orphan = load_skills(settings)[0].model_copy(update={"id": "owner-x/repo-x/nope"})
    assert read_skill_md(settings, orphan) is None


def test_skill_md_capped_for_the_llm(settings):
    """Only the head of a huge SKILL.md reaches the prompt."""
    skill = load_skills(settings)[0]
    path = skill_md_path(settings, skill)
    path.write_text("x" * 100000, encoding="utf-8")
    assert len(read_skill_md(settings, skill)) == data_mod.MD_MAX_CHARS


def make_settings(tmp_path) -> Settings:
    """An isolated artifacts dir + snapshot dir under tmp_path."""
    return Settings(output_dir=tmp_path / "out", data_dir=tmp_path / "skills-sh")


def test_raises_without_dataset(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_skills(Settings(data_dir=tmp_path / "empty"))


def test_sync_refuses_to_wipe_foreign_data(tmp_path, monkeypatch):
    """A non-empty data dir that is not a dataset directory must not be deleted by sync."""
    settings = make_settings(tmp_path)
    data_dir = settings.data_dir
    data_dir.mkdir(parents=True)
    (data_dir / "user-file.txt").write_text("precious", encoding="utf-8")

    monkeypatch.setattr(data_mod, "download_file", fake_download([]))
    with pytest.raises(RuntimeError, match="not a dataset directory"):
        sync_data(settings)
    assert (data_dir / "user-file.txt").read_text(encoding="utf-8") == "precious"


def test_sync_unpacks_only_what_a_run_reads(tmp_path, monkeypatch):
    """One tarball request fills the data dir with the index and every SKILL.md;
    the rest of the branch (hundreds of MB of skill repos) is left in the archive."""
    settings = make_settings(tmp_path)
    served = fake_download([
        {"id": "o/r/s", "name": "s", "installs": "1", "source": "o/r", "hash": "h"},
    ])
    seen = []

    def recording(url: str, dest: Path) -> bool:
        seen.append(url)
        return served(url, dest)

    monkeypatch.setattr(data_mod, "download_file", recording)
    report = sync_data(settings)
    assert seen == [TARBALL_URL]
    assert (report.data_dir / "skills.jsonl").exists()
    assert (report.data_dir / "skills" / "o" / "r" / "s" / "SKILL.md").exists()
    assert not (report.data_dir / "skills" / "o" / "r" / "s" / "extra.md").exists()
    assert report.downloaded
    assert report.tag == DIST_BRANCH  # no tags upstream: the branch itself
    assert report.seconds > 0
    assert load_skills(settings)[0].id == "o/r/s"
    assert read_skill_md(settings, load_skills(settings)[0]) is not None


def test_latest_pointer_names_the_newest_tag(latest_pointer):
    """Upstream's `latest` file is one line: one tiny request answers a sync."""
    calls = latest_pointer(b"dist-2026-09-09\n")
    assert latest_dist_tag() == "dist-2026-09-09"
    assert calls == [LATEST_URL]


def test_latest_pointer_tolerates_trailing_whitespace(latest_pointer):
    latest_pointer(b"  dist-2026-09-09  \n")
    assert latest_dist_tag() == "dist-2026-09-09"


def test_latest_pointer_rejects_anything_but_a_tag(latest_pointer):
    """A cached 404 page is not a ref a download could use, so it is ignored."""
    latest_pointer(b"<!doctype html><title>404: Not Found</title>")
    assert latest_dist_tag() is None


def test_unreadable_pointer_is_not_fatal(latest_pointer):
    """Only the shortcut is lost: the branch is always a valid fallback ref."""
    latest_pointer(b"", httpx.ConnectError("no route"))
    assert latest_dist_tag() is None


def _seed_dataset(settings) -> None:
    settings.data_dir.mkdir(parents=True)
    (settings.data_dir / "skills.jsonl").write_text("[]\n", encoding="utf-8")


def test_download_logs_never_carry_a_presigned_query(tmp_path, caplog, monkeypatch):
    """A generated image's url holds a token and a signature in its query."""
    def unreachable(method, url, **kwargs):
        raise httpx.ConnectError("no route")

    monkeypatch.setattr(data_mod.httpx, "stream", unreachable)
    monkeypatch.setattr(data_mod.time, "sleep", lambda _s: None)
    caplog.set_level("INFO")
    with pytest.raises(RuntimeError) as excinfo:
        data_mod.download_file("https://cdn.example/x.png?X-Amz-Signature=secret123",
                               tmp_path / "out.png")

    assert "https://cdn.example/x.png" in caplog.text, "the fetch stays identifiable"
    assert "secret123" not in caplog.text and "secret123" not in str(excinfo.value)


def test_url_without_query_keeps_the_path_readable():
    assert data_mod.url_without_query("https://cdn.example/a/b.png?token=x#f") == (
        "https://cdn.example/a/b.png")


def test_sync_skips_download_when_the_tag_is_unchanged(tmp_path, monkeypatch):
    """A local snapshot already at the newest tag is not downloaded or pruned."""
    settings = make_settings(tmp_path)
    _seed_dataset(settings)
    (settings.data_dir / "SNAPSHOT.json").write_text(json.dumps({"ref": "dist-2026-09-09"}))
    monkeypatch.setattr(data_mod, "latest_dist_tag", lambda: "dist-2026-09-09")

    called = []
    def no_download(url: str, dest: Path) -> bool:
        called.append(url)
        raise AssertionError("sync should not download when the tag is unchanged")
    monkeypatch.setattr(data_mod, "download_file", no_download)

    report = sync_data(settings)
    assert called == []
    assert not report.downloaded  # cache hit: tag unchanged
    assert report.tag == "dist-2026-09-09"
    assert report.seconds == 0.0


def _serve(seen: list[str], entry: dict):
    """Stand-in for data.download_file: writes a real tarball at any url."""
    def _download(url: str, dest: Path) -> bool:
        seen.append(url)
        make_tarball(Path(dest), [entry])
        return True
    return _download


def test_sync_downloads_the_tag_the_pointer_names(tmp_path, monkeypatch, latest_pointer):
    """The pointer names the ref to fetch: a moved pointer is a different snapshot."""
    settings = make_settings(tmp_path)
    _seed_dataset(settings)
    (settings.data_dir / "SNAPSHOT.json").write_text(json.dumps({"ref": "dist-2026-09-08"}))
    latest_pointer(b"dist-2026-09-09\n")
    entry = {"id": "o/r/s", "name": "s", "installs": "1", "source": "o/r", "hash": "h"}
    seen: list[str] = []
    monkeypatch.setattr(data_mod, "download_file", _serve(seen, entry))
    report = sync_data(settings)
    assert seen == [tarball_url("dist-2026-09-09")]
    assert report.downloaded
    assert report.tag == "dist-2026-09-09"
    assert read_marker(settings.data_dir).get("ref") == "dist-2026-09-09"


def test_sync_redownloads_when_the_tag_changed(tmp_path, monkeypatch):
    settings = make_settings(tmp_path)
    _seed_dataset(settings)
    (settings.data_dir / "SNAPSHOT.json").write_text(json.dumps({"ref": "dist-2026-09-08"}))
    monkeypatch.setattr(data_mod, "latest_dist_tag", lambda: "dist-2026-09-09")
    entry = {"id": "o/r/s", "name": "s", "installs": "1", "source": "o/r", "hash": "h"}
    seen: list[str] = []
    monkeypatch.setattr(data_mod, "download_file", _serve(seen, entry))
    sync_data(settings)
    assert seen == [tarball_url("dist-2026-09-09")]
    assert read_marker(settings.data_dir).get("ref") == "dist-2026-09-09"


def test_sync_refresh_forces_a_download(tmp_path, monkeypatch):
    settings = make_settings(tmp_path)
    _seed_dataset(settings)
    (settings.data_dir / "SNAPSHOT.json").write_text(json.dumps({"ref": "dist-2026-09-09"}))
    monkeypatch.setattr(data_mod, "latest_dist_tag", lambda: "dist-2026-09-09")
    entry = {"id": "o/r/s", "name": "s", "installs": "1", "source": "o/r", "hash": "h"}
    seen: list[str] = []
    monkeypatch.setattr(data_mod, "download_file", _serve(seen, entry))
    sync_data(settings, refresh=True)
    assert seen == [tarball_url("dist-2026-09-09")]
    assert read_marker(settings.data_dir).get("ref") == "dist-2026-09-09"


def test_sync_without_tags_always_downloads(tmp_path, monkeypatch):
    """Fallback to the branch when upstream publishes no tags: always re-fetch."""
    settings = make_settings(tmp_path)
    entry = {"id": "o/r/s", "name": "s", "installs": "1", "source": "o/r", "hash": "h"}
    seen: list[str] = []
    monkeypatch.setattr(data_mod, "download_file", _serve(seen, entry))
    sync_data(settings)
    assert seen == [TARBALL_URL]
    assert read_marker(settings.data_dir).get("ref") == DIST_BRANCH


def test_sync_replaces_the_previous_snapshot(tmp_path, monkeypatch):
    """Sync is wholesale: files that are gone upstream are gone locally too."""
    settings = make_settings(tmp_path)
    data_dir = settings.data_dir
    data_dir.mkdir(parents=True)
    (data_dir / "skills.jsonl").write_text(
        json.dumps({"id": "o/r/s", "name": "s", "installs": "1",
                    "source": "o/r", "hash": "old"}) + "\n", encoding="utf-8")
    stale = data_dir / "skills" / "o" / "r" / "gone" / "SKILL.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale", encoding="utf-8")

    monkeypatch.setattr(data_mod, "download_file", fake_download([
        {"id": "o/r/s", "name": "s", "installs": "1", "source": "o/r", "hash": "h"},
    ]))
    sync_data(settings)
    assert not stale.exists()
    assert load_skills(settings)[0].hash == "h"


def test_sync_keeps_results_even_when_stale(tmp_path, monkeypatch):
    """Sync is a pure data operation: results whose recorded hash changed, whose
    skill vanished upstream, or whose directory is missing all survive; spotting
    them is `stale_result_ids`'s job, dropping them `invalidate --stale`'s."""
    settings = make_settings(tmp_path)
    results_root = settings.output_dir / "skills"

    def make_result(skill_id: str) -> None:
        d = results_root / skill_id.replace(":", "_")
        d.mkdir(parents=True)
        (d / "domain.json").write_text("{}", encoding="utf-8")

    make_result("o/r/unchanged")
    make_result("o/r/changed")
    make_result("o/r/gone")

    write_index(settings, {sid: {"id": sid, "hash": h} for sid, h in {
        "o/r/unchanged": "h1",
        "o/r/changed": "old",
        "o/r/gone": "h2",
        "o/r/dirless": "h3",
    }.items()})

    monkeypatch.setattr(data_mod, "download_file", fake_download([
        {"id": "o/r/unchanged", "name": "u", "installs": "1", "source": "o/r", "hash": "h1"},
        {"id": "o/r/changed", "name": "c", "installs": "2", "source": "o/r", "hash": "new"},
        {"id": "o/r/other", "name": "x", "installs": "3", "source": "o/r", "hash": "h9"},
    ]))
    sync_data(settings)
    for skill_id in ("o/r/unchanged", "o/r/changed", "o/r/gone"):
        assert (results_root / skill_id.replace(":", "_") / "domain.json").exists()
    assert load_hashes(settings) == {
        "o/r/unchanged": "h1", "o/r/changed": "old", "o/r/gone": "h2", "o/r/dirless": "h3",
    }

    # changed and vanished ids are stale (dirless is gone from the index too);
    # only unchanged still matches the snapshot
    assert stale_result_ids(settings) == ["o/r/changed", "o/r/dirless", "o/r/gone"]


def test_stale_result_ids_needs_a_snapshot(tmp_path):
    """Without a synced snapshot there is nothing to compare against."""
    with pytest.raises(FileNotFoundError):
        stale_result_ids(make_settings(tmp_path))
