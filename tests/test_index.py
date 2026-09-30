"""index.py: the catalog - the mirror's rows joined with the label - and the report beside it."""

import json

import pytest

import common
import index
import readme
from conftest import SKILLS, skill_md_text, skill_path

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"
DOT = "owner-e/.dotcfg/settings"
# the id is the mirror's own spelling, `name` is what its SKILL.md says, and here the tree's
# directory takes the same spelling as the id - the common case
HOTEL = "owner-h/repo-h/hotel:sub"

DOMAIN = {"domain": "office-productivity", "confidence": 0.9,
          "probabilities": {"office-productivity": 0.9, "other": 0.1}}


def alpha_source() -> str:
    """The SKILL.md the fixture tree holds for `alpha`."""
    text = skill_md_text(next(e for e in SKILLS if e["id"] == ALPHA))
    assert text is not None
    return text


ALPHA_ROW = {
    "id": ALPHA,
    "name": "alpha",
    "dir": ALPHA,
    "installs": "300",
    "description": "Tidies a note list, folds the loose ends into a running index, and keeps "
                   "the whole pile searchable.",
    "description_zh": None,
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
    """The mirror's row forwarded field by field, plus the two it cannot know: the description out
    of the skill itself, and the domain one category of the closed set."""
    config = common.Config()
    common.write_json(common.angle_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    assert indexed(config)[0] == ALPHA_ROW


def test_every_buildable_skill_the_mirror_lists_is_a_row(workdir):
    """The catalog is the dataset, not the work in progress: every listed skill the tree can still
    build is a row, in the mirror's order - the batch's own - whether or not its source is fetched
    yet. `delta`'s repository is on disk and yielded nothing, so its row is gone."""
    assert [line["id"] for line in indexed(common.Config())] == [
        ALPHA, BETA, "owner-c/repo-c/gamma", HOTEL, DOT]


def test_a_listed_skill_whose_repository_is_not_on_disk_is_a_row_of_nulls(workdir):
    """A listed skill the tree has not reached yet is a row of `null`s rather than a missing row:
    the batch walks the catalog to know what to build next."""
    config = common.Config()
    listing = config.output_dir / "fresh.jsonl"
    listing.write_text('{"id": "owner-f/repo-f/foxtrot", "name": "foxtrot", "installs": 5}\n',
                       encoding="utf-8")

    lines = index.rows(config, listing)

    assert [line["id"] for line in lines] == ["owner-f/repo-f/foxtrot"]
    assert lines[0]["description"] is None
    assert lines[0]["domain"] is None


def test_the_description_is_read_out_of_the_skill_itself(workdir):
    """Upstream's index has no description any more, so the one in the row is the front matter's -
    read as YAML."""
    config = common.Config()
    source = skill_path(config.output_dir, BETA) / "SKILL.md"
    source.write_text("---\nname: beta\ndescription: >-\n  Drafts a release\n  note.\n---\n\nBody.\n",
                      encoding="utf-8")
    assert row(config, BETA)["description"] == "Drafts a release note."


def test_a_listed_skill_whose_repository_yields_nothing_is_no_row(workdir):
    """`delta` is listed, but its repository is on disk and yielded no source for it: no run can
    ever build it, so the row is gone rather than a `null` one diluting the dataset."""
    assert "owner-d/repo-d/delta" not in [line["id"] for line in indexed(common.Config())]


def test_a_source_that_yields_no_description_is_no_row(workdir):
    """A source whose front matter yields no description can never lead a build: with its
    repository already fetched, the row is gone with it."""
    config = common.Config()
    source = skill_path(config.output_dir, ALPHA) / "SKILL.md"
    source.write_text("---\nname: alpha\n---\n\nBody.\n", encoding="utf-8")

    assert ALPHA not in [line["id"] for line in indexed(common.Config())]


def test_the_domain_is_null_until_it_is_built(workdir):
    """Half the dataset is unlabelled at any moment, and the row says so: `.domain != null` is the
    finished part."""
    config = common.Config()
    assert row(config, ALPHA)["domain"] is None

    common.write_json(common.angle_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert row(config, ALPHA)["domain"] == "office-productivity"
    assert row(config, ALPHA)["confidence"] == 0.9  # how sure the endpoint was, beside the label
    assert row(config, BETA)["domain"] is None
    assert row(config, BETA)["confidence"] is None


def test_the_chinese_description_is_read_out_of_the_zh_page(workdir):
    """There is no second file holding the Chinese description: it is the `description` in the
    zh page's own front matter, `null` in the row until skill_zh.py wrote the page."""
    config = common.Config()
    assert row(config, BETA)["description_zh"] is None

    from conftest import write_zh_page
    write_zh_page(config.output_dir, BETA, "根据已合并的拉取请求起草发布说明。")

    beta = row(config, BETA)
    assert beta["description_zh"] == "根据已合并的拉取请求起草发布说明。"
    assert beta["domain"] is None  # the two angles are built independently

    assert row(config, ALPHA)["description_zh"] is None


def test_the_id_is_the_mirrors_own_spelling(workdir):
    """A row keeps the mirror's id verbatim; the `dir` field is the handle the batch is handed,
    resolved by matching the row's `name` against the sources its repository holds."""
    config = common.Config()
    hotel = row(config, HOTEL)
    assert hotel["id"] == HOTEL
    assert hotel["name"] == "hotel:sub"
    assert hotel["dir"] == HOTEL
    assert skill_path(config.output_dir, HOTEL).is_dir()


def test_a_profile_the_mirror_dropped_is_not_a_row(workdir):
    """Upstream delisting a skill unpicks its row, the same rule as any skill without a readable
    description - its source is gone with the snapshot, so nothing could be rebuilt. The label
    paid for stays on disk; it is just not listed."""
    config = common.Config()
    common.write_json(common.angle_path(config, "owner-z/repo-z/zeta", common.DOMAIN_ANGLE),
                      DOMAIN)

    lines = indexed(config)

    assert len(lines) == 5  # the mirror's own rows, and nothing beside them
    assert "owner-z/repo-z/zeta" not in [line["id"] for line in lines]
    assert common.angle_path(config, "owner-z/repo-z/zeta", common.DOMAIN_ANGLE).is_file()


# -------------------------------------------------------------------- the file


def test_a_missing_catalog_says_what_to_run(workdir):
    """Without the catalog - the listing's only lasting trace - there is no dataset to label, and
    the fix is one command, not a traceback and not a catalog of nothing."""
    (common.Config().output_dir / common.INDEX).unlink()
    with pytest.raises(SystemExit, match="just sync"):
        index.rows(common.Config())


def test_a_missing_fresh_listing_says_what_to_run(workdir):
    """A listing path that names nothing is a sync that never completed."""
    with pytest.raises(SystemExit, match="just sync"):
        index.rows(common.Config(), common.Config().output_dir / "nowhere.jsonl")


def test_a_fresh_listing_is_the_left_side(workdir):
    """The listing `just sync` hands over decides the row set, the order and the installs -
    every listed skill the tree can still build is a row, in the listing's own order, a source or
    not."""
    listing = common.Config().output_dir / "fresh.jsonl"
    listing.write_text(
        '{"id": "owner-e/.dotcfg/settings", "name": "settings", "installs": 5}\n'
        '{"id": "owner-a/repo-a/alpha", "name": "alpha", "installs": 9}\n'
        '{"id": "owner-f/repo-f/foxtrot", "name": "foxtrot", "installs": 7}\n', encoding="utf-8")

    lines = index.rows(common.Config(), listing)

    assert [line["id"] for line in lines] == [DOT, ALPHA, "owner-f/repo-f/foxtrot"]
    assert lines[0]["installs"] == 5  # the fresh listing's installs joined in
    assert lines[0]["description"]  # a fetched source fills its description in
    assert lines[2]["description"] is None  # an unfetched skill is a row of nulls
    assert "fetchedAt" not in lines[0]  # upstream dropped it, the row does not carry it


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
    common.write_json(common.angle_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert index.main([]) == 0

    catalog = config.output_dir / common.INDEX
    first = json.loads(catalog.read_text(encoding="utf-8").splitlines()[0])
    assert first["domain"] == "office-productivity"
    assert first["confidence"] == 0.9
    assert first["description_zh"] is None  # the second angle has not been built in this tree
    assert "probabilities" not in first  # the row takes what a consumer uses, the profile keeps it
    assert "indexed ->" in capsys.readouterr().err


# ------------------------------------------------------------------ the numbers


def facts(config) -> dict:
    """The numbers the README is said from, over the catalog's own rows."""
    return index.facts(config, index.rows(config))


def test_the_numbers_count_each_angle_independently(workdir):
    """They read the tree the way each batch does, so domain and translation can have different
    coverage: two labels and one translation here mean two built and one translated."""
    config = common.Config()
    common.write_json(common.angle_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.write_json(common.angle_path(config, BETA, common.DOMAIN_ANGLE), DOMAIN)
    from conftest import write_zh_page
    write_zh_page(config.output_dir, ALPHA, "中文描述")

    numbers = facts(config)

    assert (numbers["built"], numbers["total"]) == ("2", "5")
    assert numbers["percent"] == "40.0%"
    assert (numbers["skillzh"], numbers["skillzh_percent"]) == ("1", "20.0%")


def test_the_denominator_is_the_buildable_dataset(workdir):
    """The counts are over the mirror's rows the tree can still build - unfetched ones included,
    the ones whose repository yielded nothing excluded - so the numbers say how much of the real
    dataset is done rather than how much of the tree happens to be fetched."""
    numbers = facts(common.Config())

    assert (numbers["described"], numbers["total"]) == ("5", "5")


def test_a_leftover_directory_is_not_progress(workdir):
    """Only the json counts: a directory without it is not work on disk."""
    config = common.Config()
    common.write_json(common.angle_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.angle_path(config, ALPHA, common.DOMAIN_ANGLE).unlink()

    assert facts(config)["built"] == "0"


def test_a_profile_the_mirror_dropped_is_not_coverage(workdir):
    """A dropped skill keeps the label paid for on disk, but it is not in the catalog, so it is in
    neither side of the count."""
    config = common.Config()
    common.write_json(common.angle_path(config, "owner-z/repo-z/zeta", common.DOMAIN_ANGLE),
                      DOMAIN)

    numbers = facts(config)

    assert numbers["built"] == "0"
    assert (numbers["described"], numbers["total"]) == ("5", "5")


def test_the_installs_share_weighs_the_same_count(workdir):
    """The batch works the most installed first, so the count says how much is left and the weight
    says what that is worth: `alpha` and `beta` carry 500 of the 690 installs the buildable rows
    hold."""
    config = common.Config()
    common.write_json(common.angle_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.write_json(common.angle_path(config, BETA, common.DOMAIN_ANGLE), DOMAIN)

    assert facts(config)["installs"] == "72.5%"


def test_the_same_tree_reads_the_same_numbers(workdir):
    """Everything in them is a function of the tree, so a run that changed nothing writes the same
    bytes - which is what keeps `publish-dist` from spending a version number on a tree it has."""
    config = common.Config()
    common.write_json(common.angle_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert facts(config) == facts(config)


def test_the_readmes_are_written_whole_or_absent(workdir, capsys):
    """They land beside the catalog, by the same rename: a reader never sees half of one."""
    config = common.Config()
    common.write_json(common.angle_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert index.main([]) == 0

    for name in (readme.README, readme.README_ZH):
        path = config.output_dir / name
        assert path.read_text(encoding="utf-8").startswith("# skills-profiles\n")
        assert not path.with_name(path.name + ".part").exists()
    assert "readme ->" in capsys.readouterr().err


def test_a_root_skill_counts_as_built(workdir):
    """A single-skill repository keeps its source and its angles at the repository's root, one
    segment shallower than every other skill - and the numbers count it like any other."""
    config = common.Config()
    d = config.output_dir / common.SKILLS_DIR / "owner-r/repo-r"
    d.mkdir(parents=True)
    common.write_json(d / common.ANGLE_FILES[common.DOMAIN_ANGLE], DOMAIN)
    indexed = [{"id": "owner-r/repo-r/alpha", "name": "alpha", "installs": "1",
                "dir": "owner-r/repo-r", "description": "D.", "description_zh": None,
                "domain": None, "confidence": None}]

    numbers = index.facts(config, indexed)

    assert (numbers["built"], numbers["total"]) == ("1", "1")
