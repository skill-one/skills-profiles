"""readme.py: the page published with the dataset - one document, said in two languages."""

from string import Template

import gen
import index
import readme

ALPHA = "owner-a/repo-a/alpha"
DOMAIN = {"domain": ["office-productivity"], "reason": "Because it tidies notes"}
# the renderer's own slots, inside the bullet template: filled per line rather than from the numbers
SLOTS = {"label", "value"}


def numbers(config) -> dict:
    return index.facts(config, index.rows(config))


def page(config, lang: str) -> str:
    return readme.page(numbers(config), lang)


def test_the_two_languages_hold_the_same_keys():
    """The renderer reads them by name, so a key one language has and the other does not is a
    KeyError at publish time rather than an untranslated line."""
    assert set(readme.TEXT["en"]) == set(readme.TEXT["zh"])


def test_every_placeholder_is_a_number_the_page_has(workdir):
    """A page is a template over the numbers: a name that is not in them would render as a crash on
    the way out, which is the worst place to find a typo."""
    known = set(numbers(gen.Config())) | SLOTS
    for lang, text in readme.TEXT.items():
        for name, template in text.items():
            if isinstance(template, str):
                assert set(Template(template).get_identifiers()) <= known, (lang, name)


def test_the_page_is_the_front_door_of_the_published_root(workdir):
    """Everything a reader needs to use the directory without leaving it: what the layers are, what
    the angles are, how far the batch got, and the two queries that open it up."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)

    text = page(config, "en")

    assert text.startswith("# skills-profiles\n")
    assert "`skills/<id>/`" in text and "`profiles/<id>/`" in text
    assert "`domain` is one to three English tags" in text
    assert "| `domain` | 1 | 5 | 20.0% | 43.5% |" in text
    assert "| **total** | 1 | 30 | 3.3% |  |" in text
    assert "jq -r '[.id, .installs, (.domain[0] // \"-\")] | @tsv' skills.jsonl" in text


def test_the_page_says_it_is_generated(workdir):
    """It is overwritten by every `just index`, so a reader has to be told not to write in it."""
    assert "generated, so the next run overwrites it" in page(gen.Config(), "en")
    assert "下一次运行会覆盖它" in page(gen.Config(), "zh")


def test_the_chinese_page_is_the_same_document(workdir):
    """A translation is not a summary: same sections, same numbers, the prose in the other
    language - and each page points at the other."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)

    zh = page(config, "zh")

    assert "## 进度" in zh and "## 怎么用" in zh
    assert "| `domain` | 1 | 5 | 20.0% | 43.5% |" in zh
    assert "[README.md](README.md)" in zh
    assert "[README.zh-CN.md](README.zh-CN.md)" in page(config, "en")


def test_a_tree_with_nothing_built_still_has_a_page(workdir):
    """The first run of a fresh tree has no profiles at all, and the page is still a page: the
    angles are there at zero, and the numbers with nothing behind them are one dash."""
    text = page(gen.Config(), "en")

    assert "| `domain` | 0 | 5 | 0.0% | 0.0% |" in text
    assert "- **snapshot**: `\u2014`, \u2014" in text


def test_the_same_tree_writes_the_same_pages(workdir):
    """Both are functions of the tree, so nothing here can make a publish look like a change."""
    config = gen.Config()
    gen.write(config, "domain", ALPHA, DOMAIN)

    assert page(config, "en") == page(config, "en")
    assert page(config, "zh") == page(config, "zh")
