"""stale.py: the profiles a new snapshot invalidates, and the ones it does not."""

import json
from pathlib import Path

import gen
import stale

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"

DOMAIN = {"domain": "办公效率", "reason": "因为"}


def index_of(config: gen.Config) -> Path:
    """The new snapshot's own listing, which is what a comparison is made against."""
    return config.data_dir / stale.INDEX


def write_index(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8")


def previous(path: Path, entries: list[dict]) -> Path:
    """The index of the snapshot that was replaced."""
    write_index(path, entries)
    return path


# ------------------------------------------------------------------- the diff


def test_a_changed_hash_retires_that_skill_only(workdir, capsys):
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    gen.write(config, "domain", BETA, DOMAIN)
    before = previous(workdir / "previous.jsonl",
                      [{"id": ALPHA, "hash": "old"}, {"id": BETA, "hash": "same"}])
    write_index(index_of(config),
                [{"id": ALPHA, "hash": "new"}, {"id": BETA, "hash": "same"}])

    assert stale.main([str(before)]) == 0

    assert not gen.skill_dir(config, ALPHA).exists()
    assert gen.skill_dir(config, BETA).is_dir()
    captured = capsys.readouterr()
    assert captured.out.split() == [ALPHA]
    assert "retired 1 skill(s)" in captured.err


def test_a_skill_that_vanished_keeps_its_profiles(workdir, capsys):
    """Upstream dropping a skill is not a reason to throw away what it already paid for: the
    profiles stay, even though nothing can rebuild them."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    before = previous(workdir / "previous.jsonl", [{"id": ALPHA, "hash": "old"}])
    write_index(index_of(config), [{"id": BETA, "hash": "new"}])

    assert stale.main([str(before)]) == 0

    assert gen.skill_dir(config, ALPHA).is_dir()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "retired 0 skill(s)" in captured.err


def test_a_skill_with_no_hash_saved_is_not_compared(workdir):
    """The scraper saves no content hash for a skill it could not fetch, so there is nothing to
    compare for it - and it is never retired by a comparison it is not part of."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    before = previous(workdir / "previous.jsonl", [{"id": ALPHA}])
    write_index(index_of(config), [{"id": ALPHA, "hash": "new"}])

    assert stale.main([str(before)]) == 0

    assert gen.skill_dir(config, ALPHA).is_dir()


def test_a_retired_skill_that_was_never_built_retires_nothing(workdir, capsys):
    """The hash moves before anything was generated for it: the tree has nothing to drop, and
    saying so is the whole report."""
    config = gen.Config()
    before = previous(workdir / "previous.jsonl", [{"id": ALPHA, "hash": "old"}])
    write_index(index_of(config), [{"id": ALPHA, "hash": "new"}])

    assert stale.main([str(before)]) == 0

    assert capsys.readouterr().out == ""


# ------------------------------------------------------------------ the edges


def test_the_first_sync_has_nothing_to_compare(workdir, capsys):
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)

    assert stale.main([str(workdir / "nowhere.jsonl")]) == 0

    assert gen.skill_dir(config, ALPHA).is_dir()
    assert "nothing to retire" in capsys.readouterr().err


def test_a_snapshot_without_an_index_has_nothing_to_compare(workdir, capsys):
    config = gen.Config()
    index_of(config).unlink()
    before = previous(workdir / "previous.jsonl", [{"id": ALPHA, "hash": "old"}])

    assert stale.main([str(before)]) == 0

    assert "nothing to retire" in capsys.readouterr().err
