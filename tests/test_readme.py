"""readme.py: the page published with the dataset - one short document, said in two languages."""

from string import Template

import common
import index
import readme

ALPHA = "owner-a/repo-a/alpha"
DOMAIN = {"domain": "office-productivity"}
# the renderer's own slots, inside the bullet template: filled per line rather than from the numbers
SLOTS = {"label", "value"}
# the page is the front door of a published directory, not a document: the way in, the progress,
# and the two lines saying which tree it describes
LINES = 17


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
    known = set(numbers(common.Config())) | SLOTS
    for lang, text in readme.TEXT.items():
        for name, template in text.items():
            if isinstance(template, str):
                assert set(Template(template).get_identifiers()) <= known, (lang, name)


def test_the_page_stays_a_page(workdir):
    """It is the front door of a published directory rather than a document about the project."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert len(page(config, "en").splitlines()) <= LINES
    assert len(page(config, "zh").splitlines()) <= LINES


def test_the_page_opens_the_directory_it_sits_in(workdir):
    """A reader who lands on the published root gets the two things they need before the numbers:
    which files are the skill and which are what was written about it, and how far the batch got."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.write_json(common.profile_path(config, ALPHA, common.TRANSLATE_ANGLE),
                      {"description_zh": "中文描述"})

    text = page(config, "en")

    assert text.startswith("# skills-profiles\n")
    assert "`skills/<id>/` is the skill as published" in text
    assert "`profiles/<id>/` holds what is written about it" in text
    assert "`description_zh`" in text
    assert "- **domain**: 1 of 5 labelled (20.0%), covering 43.5% of the mirror's installs" in text
    assert "- **translate**: 1 of 5 translated (20.0%), covering 43.5% of the mirror's installs" in text


def test_the_page_says_it_is_generated(workdir):
    """It is overwritten by every `just index`, so a reader has to be told not to write in it."""
    assert "Written by `just index` -" in page(common.Config(), "en")
    assert "由 `just index` 从这棵树生成" in page(common.Config(), "zh")


def test_the_chinese_page_is_the_same_document(workdir):
    """A translation is not a summary: same sections, same numbers, the prose in the other language
    - and each page points at the other."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)
    common.write_json(common.profile_path(config, ALPHA, common.TRANSLATE_ANGLE),
                      {"description_zh": "中文描述"})

    zh = page(config, "zh")

    assert "## 进度" in zh
    assert "5 个里已标 1 个（20.0%），覆盖镜像安装量的 43.5%" in zh
    assert "5 个里已翻译 1 个（20.0%），覆盖镜像安装量的 43.5%" in zh
    assert "[README.md](README.md)" in zh
    assert "[README.zh-CN.md](README.zh-CN.md)" in page(config, "en")


def test_a_tree_with_nothing_built_still_has_a_page(workdir):
    """The first run of a fresh tree has no labels at all, and the page is still a page: the count
    is zero and the numbers with nothing behind them are one dash."""
    text = page(common.Config(), "en")

    assert "- **domain**: 0 of 5 labelled (0.0%), covering 0.0% of the mirror's installs" in text
    assert "- **translate**: 0 of 5 translated (0.0%), covering 0.0% of the mirror's installs" in text
    assert "- **snapshot**: `—`, —" in text


def test_the_same_tree_writes_the_same_pages(workdir):
    """Both are functions of the tree, so nothing here can make a publish look like a change."""
    config = common.Config()
    common.write_json(common.profile_path(config, ALPHA, common.DOMAIN_ANGLE), DOMAIN)

    assert page(config, "en") == page(config, "en")
    assert page(config, "zh") == page(config, "zh")
