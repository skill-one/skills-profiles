"""index.py: the flat jsonl view of the domain that labels a skill."""

import json

import gen
import index

ALPHA = "owner-a/repo-a/alpha"
BETA = "owner-b/repo-b/beta"
HOTEL = "owner-h/repo-h/hotel:sub"
HOTEL_DIR = "owner-h/repo-h/hotel_sub"  # the spelling a `:` takes in the tree, and so its id
DOT = "owner-e/.dotcfg/settings"

DOMAIN = {"domain": "办公效率", "reason": "因为"}


def indexed(config) -> list[dict]:
    """The index as a reader sees it: write it, then read the lines back."""
    path = index.write(config, index.rows(config))
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


# ------------------------------------------------------------------- the graph


def test_the_graph_is_the_output_tree_in_path_order(workdir):
    """The listing is the tree: a skill is one because it has a directory, and one under a
    repo named `.dotcfg` is there the whole time - which is why the walk is not a glob."""
    config = gen.Config()
    for skill in (HOTEL, DOT, BETA, ALPHA):
        gen.write(config, "domain", skill, DOMAIN)
    assert index.skill_ids(config) == [ALPHA, BETA, DOT, HOTEL_DIR]


def test_the_index_needs_nothing_fetched(workdir, monkeypatch):
    """It reads the output tree alone, so a checkout of published profiles indexes without the
    snapshot the batch needs."""
    gen.write(gen.Config(), "domain", ALPHA, DOMAIN)
    monkeypatch.setenv("SKILLS_PROFILES_DATA_DIR", str(workdir / "nowhere" / "skills-sh"))
    assert [row["id"] for row in index.rows(gen.Config())] == [ALPHA]


def test_the_id_is_the_spelling_the_tree_is_named_in(workdir):
    """The row's id is the directory's own path, because that is the spelling upstream writes
    and the one the batch is handed - a consumer joins on it either way."""
    config = gen.Config()
    gen.write(config, "domain", HOTEL, DOMAIN)
    assert indexed(config)[0]["id"] == HOTEL_DIR


# -------------------------------------------------------------------- the rows


def test_a_row_is_flat(workdir):
    """`domain.domain` keeps its own name at the top level, so `jq .domain` needs no path."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    assert indexed(config) == [{"id": ALPHA, "domain": "办公效率", "reason": "因为"}]


def test_an_empty_tree_indexes_nothing(config):
    """No line at all rather than an empty one: the index lists what is there."""
    assert index.rows(config) == []
    assert index.write(config, []).read_text(encoding="utf-8") == ""


def test_a_skill_whose_json_is_not_there_is_not_a_row(workdir):
    """The markdown is written first and the json renamed into place behind it, so a skill
    directory can exist with nothing the index can read - which is not a row."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    gen.json_path(config, "domain", ALPHA).unlink()
    assert index.rows(config) == []


def test_rows_are_in_path_order(workdir):
    config = gen.Config()
    for skill in (BETA, ALPHA):
        gen.write(config, "domain", skill, DOMAIN)
    assert [row["id"] for row in index.rows(config)] == [ALPHA, BETA]


# -------------------------------------------------------------------- the file


def test_write_is_whole_or_absent(workdir):
    """The file is renamed into place and every row is its own line, so a reader never sees
    half a line and a crash leaves the previous index alone."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)
    path = index.write(config, index.rows(config))

    assert path == config.output_dir / index.INDEX
    assert path.read_text(encoding="utf-8").endswith("\n")
    assert not path.with_name(path.name + ".part").exists()


def test_main_writes_and_reports_the_index(workdir, capsys):
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)

    assert index.main([]) == 0

    index_file = config.output_dir / index.INDEX
    assert json.loads(index_file.read_text(encoding="utf-8"))["domain"] == "办公效率"
    assert "indexed 1 skills" in capsys.readouterr().err
