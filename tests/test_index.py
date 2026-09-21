"""index.py: the catalog - the mirror's rows joined with what this project read and decided - and
the report written beside it."""

import json

import pytest

import gen
import index
import readme
from conftest import skill_path

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"
DOT = "owner-e/.dotcfg/settings"
# `hotel:sub` is how the mirror spells this id, and `hotel_sub` is the spelling its directories take
HOTEL = "owner-h/repo-h/hotel:sub"
HOTEL_DIR = "owner-h/repo-h/hotel_sub"

DOMAIN = {"domain": "office-productivity", "confidence": 0.9,
          "probabilities": {"office-productivity": 0.9, "other": 0.1}}
ALPHA_ROW = {
    "id": ALPHA,
    "installs": "300",
    "url": None,
    "hash": "a" * 64,
    "fetchedAt": None,
    "description": "Tidies a note list, folds the loose ends into a running index, and keeps "
                   "the whole pile searchable.",
    "domain": "office-productivity",
    "confidence": 0.9,
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
    the two fields it cannot know are added: the description out of the skill itself, and the domain
    one category of the closed set."""
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
        "fetchedAt": None, "description": None, "domain": None, "confidence": None}


def test_the_domain_is_null_until_it_is_built(workdir):
    """Half the dataset is unlabelled at any moment, and the row says so rather than leaving the
    field out: `.domain != null` is the finished part."""
    config = gen.Config()
    assert row(config, ALPHA)["domain"] is None

    gen.write(config, "domain", ALPHA, DOMAIN)

    assert row(config, ALPHA)["domain"] == "office-productivity"
    assert row(config, ALPHA)["confidence"] == 0.9  # how sure the endpoint was, beside the label
    assert row(config, BETA)["domain"] is None
    assert row(config, BETA)["confidence"] is None


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
                         "domain": "office-productivity", "confidence": 0.9}
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
    first = json.loads(catalog.read_text(encoding="utf-8").splitlines()[0])
    assert first["domain"] == "office-productivity"
    assert first["confidence"] == 0.9
    assert "probabilities" not in first  # the row takes what a consumer uses, the profile keeps the rest
    assert "indexed 6 skills" in capsys.readouterr().err


# ------------------------------------------------------------------ the numbers


def facts(config) -> dict:
    """The numbers the README is said from, over the catalog's own rows."""
    return index.facts(config, index.rows(config))


def angle(numbers: dict, name: str) -> dict:
    return next(row for row in numbers["angles"] if row["angle"] == name)


def test_the_numbers_count_the_angles_the_tree_holds(workdir):
    """They read the tree the way the batch does - an angle's json is the unit of work - so `domain`
    built for two skills of the five that can be built is what they say, and the angles nothing has
    been built for are at zero rather than left out."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    gen.write(config, "domain", BETA, DOMAIN)

    numbers = facts(config)

    assert (angle(numbers, "domain")["built"], angle(numbers, "domain")["of"]) == (2, 5)
    assert (angle(numbers, "scenario")["built"], angle(numbers, "scenario")["of"]) == (0, 5)
    assert (numbers["cells_built"], numbers["cells"]) == ("2", "30")  # six angles, five skills
    assert numbers["count"] == "6"


def test_the_denominator_is_what_can_be_built(workdir):
    """`delta` is a skill the mirror lists and never fetched, so no prompt can lead with it and the
    batch never touches it: counting it would pin the number below 100% forever."""
    numbers = facts(gen.Config())

    assert (numbers["buildable"], numbers["listed"]) == ("5", "6")
    assert angle(numbers, "domain")["of"] == 5


def test_a_leftover_directory_is_not_progress(workdir):
    """`just invalidate` deletes the files and leaves the directory behind, so counting directories
    would claim work that is not on disk."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    gen.json_path(config, "domain", ALPHA).unlink()

    assert angle(facts(config), "domain")["built"] == 0


def test_a_profile_the_mirror_dropped_is_not_coverage(workdir):
    """A dropped skill keeps the profiles that were paid for, and its row stays in the catalog - but
    it is not part of the dataset, so it is in neither side of the count."""
    config = gen.Config()
    gen.write(config, "domain", "owner-z/repo-z/zeta", DOMAIN)

    numbers = facts(config)

    assert angle(numbers, "domain")["built"] == 0
    assert (numbers["listed"], numbers["buildable"]) == ("6", "5")


def test_the_installs_share_weighs_the_same_count(workdir):
    """The batch works the most installed skills first, so the count says how much is left and the
    weight says what that is worth: `alpha` and `beta` carry 500 of the 690 installs there are."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    gen.write(config, "domain", BETA, DOMAIN)

    assert angle(facts(config), "domain")["installs"] == "72.5%"


def test_the_numbers_say_which_snapshot_they_describe(workdir):
    """The mirror's own files are its identity, and they are read: a wall clock of our own would
    make every publish a change, and a publish that changes nothing spends no version number."""
    config = gen.Config()
    upstream = config.output_dir / gen.UPSTREAM_DIR
    (upstream / "latest").write_text("dist-2026-01-02\n", encoding="utf-8")
    (upstream / "stats.json").write_text(json.dumps({
        "startedAt": "2026-01-02T03:04:05.678Z", "finishedAt": "2026-01-02T03:04:35.678Z",
        "durationMs": 30000,
    }), encoding="utf-8")

    numbers = facts(config)

    assert numbers["tag"] == "dist-2026-01-02"
    assert numbers["scan"] == "2026-01-02T03:04:05Z -> 2026-01-02T03:04:35Z (30s)"


def test_a_tree_that_cannot_answer_says_so(workdir):
    """The fixture's `upstream/` holds the mirror's index and nothing else, so the numbers with
    nothing behind them are one dash rather than a traceback or a blank."""
    numbers = facts(gen.Config())

    assert (numbers["tag"], numbers["scan"]) == ("\u2014", "\u2014")


def test_the_same_tree_reads_the_same_numbers(workdir):
    """Everything in them is a function of the tree, so a run that changed nothing writes the same
    bytes - which is what keeps `publish-dist` from spending a version number on a tree it already
    has."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)

    assert facts(config) == facts(config)


def test_the_readmes_are_written_whole_or_absent(workdir, capsys):
    """They land beside the catalog, by the same rename: a reader never sees half of one."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)

    assert index.main([]) == 0

    for name in (readme.README, readme.README_ZH):
        path = config.output_dir / name
        assert path.read_text(encoding="utf-8").startswith("# skills-profiles\n")
        assert not path.with_name(path.name + ".part").exists()
    assert "readme ->" in capsys.readouterr().err
