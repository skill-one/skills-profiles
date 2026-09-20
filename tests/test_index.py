"""index.py: the catalog - the mirror's rows joined with what this project read and decided."""

import json

import pytest

import gen
import index
from conftest import skill_path

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"
DOT = "owner-e/.dotcfg/settings"
# `hotel:sub` is how the mirror spells this id, and `hotel_sub` is the spelling its directories take
HOTEL = "owner-h/repo-h/hotel:sub"
HOTEL_DIR = "owner-h/repo-h/hotel_sub"

DOMAIN = {"domain": ["office-productivity"], "reason": "Because it tidies notes"}
ALPHA_ROW = {
    "id": ALPHA,
    "installs": "300",
    "url": None,
    "hash": "a" * 64,
    "fetchedAt": None,
    "description": "Tidies a note list, folds the loose ends into a running index, and keeps "
                   "the whole pile searchable.",
    "domain": ["office-productivity"],
    "reason": "Because it tidies notes",
}


def indexed(config) -> list[dict]:
    """The catalog as a reader sees it: write it, then read the lines back."""
    path = index.write(config, index.rows(config))
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def row(config, skill_id: str) -> dict:
    return next(line for line in indexed(config) if line["id"] == skill_id)


# -------------------------------------------------------------------- the rows


def test_a_row_is_the_mirrors_own_fields_plus_ours(workdir):
    """The mirror's row is forwarded field by field - installs, url, hash, when it was fetched - and
    the three fields it cannot know are added: the description out of the skill itself, and the
    domain with its reason."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    assert indexed(config)[0] == ALPHA_ROW


def test_every_skill_the_mirror_lists_is_a_row(workdir):
    """The catalog is the dataset, not the work in progress: it lists the skills that have no
    profiles yet, and it lists them in the mirror's order - the batch's own."""
    assert [line["id"] for line in indexed(gen.Config())] == [
        ALPHA, BETA, "owner-c/repo-c/gamma", HOTEL, DOT, "owner-d/repo-d/delta"]


def test_the_description_is_read_out_of_the_skill_itself(workdir):
    """Upstream's index has no description any more, so the one in the row is the front matter's -
    read as YAML, which is what makes a folded block or a quoted string arrive as text."""
    config = gen.Config()
    source = skill_path(config.output_dir, BETA) / "SKILL.md"
    source.write_text("---\nname: beta\ndescription: >-\n  Drafts a release\n  note.\n---\n\nBody.\n",
                      encoding="utf-8")
    assert row(config, BETA)["description"] == "Drafts a release note."


def test_a_description_nothing_can_be_read_from_is_null(workdir):
    """`delta` is a skill the scraper recorded and never fetched, so there is no `SKILL.md` to read.
    It is still the mirror's row - and `null` is how the catalog says the batch cannot touch it."""
    assert row(gen.Config(), "owner-d/repo-d/delta") == {
        "id": "owner-d/repo-d/delta", "installs": "90", "url": None, "hash": None,
        "fetchedAt": None, "description": None, "domain": None, "reason": None}


def test_the_domain_is_null_until_it_is_built(workdir):
    """Half the dataset is unlabelled at any moment, and the row says so rather than leaving the
    field out: `.domain != null` is the finished part."""
    config = gen.Config()
    assert row(config, ALPHA)["domain"] is None

    gen.write(config, "domain", ALPHA, DOMAIN)

    assert row(config, ALPHA)["domain"] == ["office-productivity"]
    assert row(config, ALPHA)["reason"] == "Because it tidies notes"
    assert row(config, BETA)["reason"] is None


def test_the_id_is_the_mirrors_own_spelling(workdir):
    """A row is joined on the mirror's id - what skills.sh and the url use - while the directories
    of the tree spell a `:` as `_`, which is the handle the batch is handed."""
    config = gen.Config()
    assert row(config, HOTEL)["id"] == HOTEL
    assert skill_path(config.output_dir, HOTEL).is_dir()


def test_a_profile_the_mirror_dropped_is_still_a_row(workdir):
    """Upstream delisting a skill does not unpick the profiles already paid for, so its row stays -
    with the fields the mirror can no longer supply left empty - and it is named the way the tree
    spells it, because that is the only spelling left."""
    config = gen.Config()
    gen.write(config, "domain", "owner-z/repo-z/zeta", DOMAIN)

    lines = indexed(config)

    assert lines[-1] == {"id": "owner-z/repo-z/zeta", "installs": None, "url": None, "hash": None,
                         "fetchedAt": None, "description": None,
                         "domain": ["office-productivity"],
                         "reason": "Because it tidies notes"}
    assert len(lines) == 7  # the six the mirror lists, plus the one it does not


def test_an_orphan_is_walked_rather_than_globbed(workdir):
    """The second population is read off the profile tree, and a glob would drop a leading dot -
    which is a repo name people use."""
    config = gen.Config()
    gen.write(config, "domain", DOT, DOMAIN)
    assert index.skill_ids(config) == [DOT]


# -------------------------------------------------------------------- the file


def test_a_missing_mirror_index_says_what_to_run(workdir):
    """Without the mirror's own listing there is no dataset to label, and the fix is one command -
    not a traceback and not a catalog of nothing."""
    (gen.Config().output_dir / index.MIRROR).unlink()
    with pytest.raises(SystemExit, match="just sync"):
        index.rows(gen.Config())


def test_a_null_is_spelled_the_way_the_justfile_matches_it(workdir):
    """`just` keeps an undescribable skill out of the window by matching `"description":null` in the
    line, so the spelling is a contract between the two."""
    config = gen.Config()
    line = index.write(config, index.rows(config)).read_text(encoding="utf-8")
    assert '"description":null' in line


def test_write_is_whole_or_absent(workdir):
    """The file is renamed into place and every row is its own line, so a reader never sees
    half a line and a crash leaves the previous catalog alone."""
    config = gen.Config()
    path = index.write(config, index.rows(config))

    assert path == config.output_dir / gen.INDEX
    assert path.read_text(encoding="utf-8").endswith("\n")
    assert not path.with_name(path.name + ".part").exists()


def test_main_writes_and_reports_the_catalog(workdir, capsys):
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)

    assert index.main([]) == 0

    catalog = config.output_dir / gen.INDEX
    first = catalog.read_text(encoding="utf-8").splitlines()[0]
    assert json.loads(first)["domain"] == ["office-productivity"]
    assert "indexed 6 skills" in capsys.readouterr().err
