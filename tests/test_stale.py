"""stale.py: the labels a new snapshot invalidates, and the ones it does not."""

import json
from pathlib import Path

import common
import stale

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"

DOMAIN = {"domain": "office-productivity"}


def index_of(config: common.Config) -> Path:
    """The catalog the sync has just rewritten, which is what a comparison is made against."""
    return config.output_dir / common.INDEX


def write_index(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8")


def previous(path: Path, entries: list[dict]) -> Path:
    """The catalog as it was before the sync: the copy `just refresh` keeps of it."""
    write_index(path, entries)
    return path


# ------------------------------------------------------------------- the diff


def test_a_changed_hash_retires_that_skill_only(workdir, capsys):
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.write_json(common.profile_path(config, BETA, common.DOMAIN_ANGLE), DOMAIN)
    before = previous(workdir / "previous.jsonl",
                      [{"id": ALPHA, "hash": "old"}, {"id": BETA, "hash": "same"}])
    write_index(index_of(config),
                [{"id": ALPHA, "hash": "new"}, {"id": BETA, "hash": "same"}])

    assert stale.main([str(before)]) == 0

    assert not common.profile_dir(config, ALPHA).exists()
    assert common.profile_dir(config, BETA).is_dir()
    captured = capsys.readouterr()
    assert captured.out.split() == [ALPHA]
    assert "retired 1 profile(s)" in captured.err


def test_a_skill_that_vanished_keeps_its_profiles(workdir, capsys):
    """Upstream dropping a skill is not a reason to throw away what it already paid for."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    before = previous(workdir / "previous.jsonl", [{"id": ALPHA, "hash": "old"}])
    write_index(index_of(config), [{"id": BETA, "hash": "new"}])

    assert stale.main([str(before)]) == 0

    assert common.profile_dir(config, ALPHA).is_dir()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "retired 0 profile(s)" in captured.err


def test_a_skill_with_no_hash_saved_is_not_compared(workdir):
    """The scraper saves no content hash for a skill it could not fetch, so there is nothing to
    compare for it - and it is never retired by a comparison it is not part of."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    before = previous(workdir / "previous.jsonl", [{"id": ALPHA}])
    write_index(index_of(config), [{"id": ALPHA, "hash": "new"}])

    assert stale.main([str(before)]) == 0

    assert common.profile_dir(config, ALPHA).is_dir()


def test_a_retired_skill_that_was_never_built_retires_nothing(workdir, capsys):
    """The hash moves before anything was generated for it: the tree has nothing to drop."""
    config = common.Config()
    before = previous(workdir / "previous.jsonl", [{"id": ALPHA, "hash": "old"}])
    write_index(index_of(config), [{"id": ALPHA, "hash": "new"}])

    assert stale.main([str(before)]) == 0

    assert capsys.readouterr().out == ""


# ------------------------------------------------------------------ the edges


def test_the_first_sync_has_nothing_to_compare(workdir, capsys):
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert stale.main([str(workdir / "nowhere.jsonl")]) == 0

    assert common.profile_dir(config, ALPHA).is_dir()
    assert "nothing to retire" in capsys.readouterr().err


def test_a_tree_without_a_catalog_has_nothing_to_compare(workdir, capsys):
    """A cold start on this side too: a sync rewrites the catalog, and one that never wrote it
    leaves nothing to compare against."""
    before = previous(workdir / "previous.jsonl", [{"id": ALPHA, "hash": "old"}])

    assert stale.main([str(before)]) == 0

    assert "nothing to retire" in capsys.readouterr().err
