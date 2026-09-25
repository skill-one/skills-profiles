"""index.py: the catalog - the mirror's rows joined with the label - and the report beside it."""

import json

import pytest

import common
import index
import readme
from conftest import skill_path

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"
DOT = "owner-e/.dotcfg/settings"
# `hotel:sub` is how the mirror spells this id, and `hotel_sub` is the spelling its directories take
HOTEL = "owner-h/repo-h/hotel:sub"

DOMAIN = {"domain": "office-productivity", "confidence": 0.9,
          "probabilities": {"office-productivity": 0.9, "other": 0.1}}
ALPHA_ROW = {
    "id": ALPHA,
    "installs": "300",
    "hash": "a" * 64,
    "fetchedAt": None,
    "description": "Tidies a note list, folds the loose ends into a running index, and keeps "
                   "the whole pile searchable.",
    "description_zh": None,
    "domain": "office-productivity",
    "confidence": 0.9,
    "skill_zh": None,
}


def indexed(config) -> list[dict]:
    """The catalog as a reader sees it: write it, then read the lines back."""
    path = index.write(config, index.rows(config))
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def row(config, skill_id: str) -> dict:
    return next(line for line in indexed(config) if line["id"] == skill_id)


# -------------------------------------------------------------------- the rows


def test_a_row_is_the_mirrors_own_fields_plus_ours(workdir):
    """The mirror's row forwarded field by field, plus the two it cannot know: the description out
    of the skill itself, and the domain one category of the closed set."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    assert indexed(config)[0] == ALPHA_ROW


def test_every_skill_the_mirror_lists_is_a_row(workdir):
    """The catalog is the dataset, not the work in progress: it lists the skills with no label yet,
    in the mirror's order - the batch's own."""
    assert [line["id"] for line in indexed(common.Config())] == [
        ALPHA, BETA, "owner-c/repo-c/gamma", HOTEL, DOT, "owner-d/repo-d/delta"]


def test_the_description_is_read_out_of_the_skill_itself(workdir):
    """Upstream's index has no description any more, so the one in the row is the front matter's -
    read as YAML."""
    config = common.Config()
    source = skill_path(config.output_dir, BETA) / "SKILL.md"
    source.write_text("---\nname: beta\ndescription: >-\n  Drafts a release\n  note.\n---\n\nBody.\n",
                      encoding="utf-8")
    assert row(config, BETA)["description"] == "Drafts a release note."


def test_a_description_nothing_can_be_read_from_is_null(workdir):
    """`delta` is a skill the scraper recorded and never fetched, so there is no `SKILL.md` to read.
    It is still the mirror's row - and `null` is how the catalog says the batch cannot touch it."""
    assert row(common.Config(), "owner-d/repo-d/delta") == {
        "id": "owner-d/repo-d/delta", "installs": "90", "hash": None,
        "fetchedAt": None, "description": None, "description_zh": None,
        "domain": None, "confidence": None, "skill_zh": None}


def test_the_domain_is_null_until_it_is_built(workdir):
    """Half the dataset is unlabelled at any moment, and the row says so: `.domain != null` is the
    finished part."""
    config = common.Config()
    assert row(config, ALPHA)["domain"] is None

    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert row(config, ALPHA)["domain"] == "office-productivity"
    assert row(config, ALPHA)["confidence"] == 0.9  # how sure the endpoint was, beside the label
    assert row(config, BETA)["domain"] is None
    assert row(config, BETA)["confidence"] is None


def test_the_chinese_description_is_null_until_it_is_built(workdir):
    """The second angle joins the same way the label does: its own file in the profile dir, `null`
    in the row until translate.py wrote it, and the Chinese text once it has."""
    config = common.Config()
    assert row(config, BETA)["description_zh"] is None

    common.write_json(common.profile_path(config, BETA, common.TRANSLATE_ANGLE),
                      {"description_zh": "根据已合并的拉取请求起草发布说明。"})

    beta = row(config, BETA)
    assert beta["description_zh"] == "根据已合并的拉取请求起草发布说明。"
    assert beta["domain"] is None  # the two angles are built independently

    assert row(config, ALPHA)["description_zh"] is None


def test_the_chinese_page_is_a_presence_marker(workdir):
    """The third angle's answer is the page itself, so the row carries only that it exists."""
    config = common.Config()
    assert row(config, ALPHA)["skill_zh"] is None

    page = common.profile_dir(config, ALPHA) / f"{common.SKILL_ZH_ANGLE}.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text("---\nname: alpha\n---\n\n中文正文。\n", encoding="utf-8")

    assert row(config, ALPHA)["skill_zh"] is True


def test_the_id_is_the_mirrors_own_spelling(workdir):
    """A row is joined on the mirror's id, while the directories of the tree spell a `:` as `_`,
    which is the handle the batch is handed."""
    config = common.Config()
    assert row(config, HOTEL)["id"] == HOTEL
    assert skill_path(config.output_dir, HOTEL).is_dir()


def test_a_profile_the_mirror_dropped_is_still_a_row(workdir):
    """Upstream delisting a skill does not unpick the label already paid for, so its row stays -
    with the mirror's fields left empty - and it is named the way the tree spells it."""
    config = common.Config()
    common.write_json(common.profile_path(config, "owner-z/repo-z/zeta", common.DOMAIN_ANGLE),
                      DOMAIN)

    lines = indexed(config)

    assert lines[-1] == {"id": "owner-z/repo-z/zeta", "installs": None, "hash": None,
                         "fetchedAt": None, "description": None, "description_zh": None,
                         "domain": "office-productivity", "confidence": 0.9, "skill_zh": None}
    assert len(lines) == 7  # the six the mirror lists, plus the one it does not


def test_an_orphan_is_walked_rather_than_globbed(workdir):
    """The second population is read off the profile tree, and a glob would drop a leading dot -
    which is a repo name people use."""
    config = common.Config()
    common.write_json(common.profile_path(config, DOT, common.DOMAIN_ANGLE), DOMAIN)
    assert index.skill_ids(config) == [DOT]


# -------------------------------------------------------------------- the file


def test_a_missing_mirror_index_says_what_to_run(workdir):
    """Without the mirror's own listing there is no dataset to label, and the fix is one command -
    not a traceback and not a catalog of nothing."""
    (common.Config().output_dir / index.MIRROR).unlink()
    with pytest.raises(SystemExit, match="just sync"):
        index.rows(common.Config())


def test_a_null_is_spelled_the_way_the_justfile_matches_it(workdir):
    """`just` keeps an undescribable skill out of the window by matching `"description":null` in the
    line, so the spelling is a contract between the two."""
    config = common.Config()
    line = index.write(config, index.rows(config)).read_text(encoding="utf-8")
    assert '"description":null' in line


def test_write_is_whole_or_absent(workdir):
    """The file is renamed into place and every row is its own line, so a reader never sees half a
    line and a crash leaves the previous catalog alone."""
    config = common.Config()
    path = index.write(config, index.rows(config))

    assert path == config.output_dir / common.INDEX
    assert path.read_text(encoding="utf-8").endswith("\n")
    assert not path.with_name(path.name + ".part").exists()


def test_main_writes_and_reports_the_catalog(workdir, capsys):
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert index.main([]) == 0

    catalog = config.output_dir / common.INDEX
    first = json.loads(catalog.read_text(encoding="utf-8").splitlines()[0])
    assert first["domain"] == "office-productivity"
    assert first["confidence"] == 0.9
    assert first["description_zh"] is None  # the second angle has not been built in this tree
    assert "probabilities" not in first  # the row takes what a consumer uses, the profile keeps it
    assert "indexed 6 skills" in capsys.readouterr().err


# ------------------------------------------------------------------ the numbers


def facts(config) -> dict:
    """The numbers the README is said from, over the catalog's own rows."""
    return index.facts(config, index.rows(config))


def test_the_numbers_count_each_angle_independently(workdir):
    """They read the tree the way each batch does, so domain and translation can have different
    coverage: two labels and one translation here mean two built and one translated."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.write_json(common.profile_path(config, BETA, common.DOMAIN_ANGLE), DOMAIN)
    common.write_json(common.profile_path(config, ALPHA, common.TRANSLATE_ANGLE),
                      {"description_zh": "中文描述"})
    page = common.profile_dir(config, BETA) / f"{common.SKILL_ZH_ANGLE}.md"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text("中文页面\n", encoding="utf-8")

    numbers = facts(config)

    assert (numbers["built"], numbers["buildable"]) == ("2", "5")
    assert numbers["percent"] == "40.0%"
    assert (numbers["translated"], numbers["translate_percent"]) == ("1", "20.0%")
    assert numbers["translate_installs"] == "43.5%"
    assert (numbers["skillzh"], numbers["skillzh_percent"]) == ("1", "20.0%")


def test_the_denominator_is_what_can_be_built(workdir):
    """`delta` is a skill the mirror lists and never fetched, so it can never be labelled: counting
    it would pin the number below 100% forever."""
    numbers = facts(common.Config())

    assert (numbers["buildable"], numbers["listed"]) == ("5", "6")


def test_a_leftover_directory_is_not_progress(workdir):
    """Only the json counts: a directory without it is not work on disk."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.profile_path(config, ALPHA, common.DOMAIN_ANGLE).unlink()

    assert facts(config)["built"] == "0"


def test_a_profile_the_mirror_dropped_is_not_coverage(workdir):
    """A dropped skill keeps the label paid for, and its row stays in the catalog - but it is not
    part of the dataset, so it is in neither side of the count."""
    config = common.Config()
    common.write_json(common.profile_path(config, "owner-z/repo-z/zeta", common.DOMAIN_ANGLE),
                      DOMAIN)

    numbers = facts(config)

    assert numbers["built"] == "0"
    assert (numbers["listed"], numbers["buildable"]) == ("6", "5")


def test_the_installs_share_weighs_the_same_count(workdir):
    """The batch works the most installed first, so the count says how much is left and the weight
    says what that is worth: `alpha` and `beta` carry 500 of the 690 installs there are."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.write_json(common.profile_path(config, BETA, common.DOMAIN_ANGLE), DOMAIN)

    assert facts(config)["installs"] == "72.5%"


def test_the_numbers_say_which_snapshot_they_describe(workdir):
    """The mirror's own files are its identity, and they are read: a wall clock of our own would
    make every publish a change."""
    config = common.Config()
    upstream = config.output_dir / common.UPSTREAM_DIR
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
    numbers = facts(common.Config())

    assert (numbers["tag"], numbers["scan"]) == ("—", "—")


def test_the_same_tree_reads_the_same_numbers(workdir):
    """Everything in them is a function of the tree, so a run that changed nothing writes the same
    bytes - which is what keeps `publish-dist` from spending a version number on a tree it has."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert facts(config) == facts(config)


def test_the_readmes_are_written_whole_or_absent(workdir, capsys):
    """They land beside the catalog, by the same rename: a reader never sees half of one."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert index.main([]) == 0

    for name in (readme.README, readme.README_ZH):
        path = config.output_dir / name
        assert path.read_text(encoding="utf-8").startswith("# skills-profiles\n")
        assert not path.with_name(path.name + ".part").exists()
    assert "readme ->" in capsys.readouterr().err
