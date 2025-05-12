import datetime
import pathlib

import pytest

from site_generator import config_test, frontmatter


def fake_page_frontmatter(**kwargs) -> frontmatter.PageFrontmatter:
    if "file" not in kwargs:
        kwargs["file"] = pathlib.Path("./pages/test.md").absolute()
    return frontmatter.PageFrontmatter(**kwargs)


@pytest.mark.parametrize(
    ("fm_kwargs", "cfg_kwargs", "expected"),
    [
        ({}, {}, ["", "default.html", "default.html"]),
        ({"template": "foo.html"}, {}, ["foo.html", "default.html", "default.html"]),
        ({}, {"default_template": "bar.html"}, ["", "default.html", "bar.html"]),
        (
            {"template": "foo.html"},
            {"default_template": "bar.html"},
            ["foo.html", "default.html", "bar.html"],
        ),
        ({"type": "blog"}, {}, ["", "blog.html", "default.html"]),
    ],
)
def test_page_frontmatter__get_template_names(
    fm_kwargs: dict, cfg_kwargs: dict, expected: list[str]
) -> None:
    fm = fake_page_frontmatter(**fm_kwargs)
    fm.config = config_test.fake_test_config(**cfg_kwargs)

    assert fm.get_template_names() == expected


def test_page_frontmatter__get_template_names__no_config() -> None:
    fm = fake_page_frontmatter()
    with pytest.raises(ValueError, match="config must be set"):
        fm.get_template_names()


@pytest.mark.parametrize(
    ("file", "expected"),
    [
        ("./pages/debug/markdown.md", "debug/markdown/index.html"),
        ("./pages/debug/index.md", "debug/index.html"),
    ],
)
def test_page_frontmatter__get_output_path(file: str, expected: str) -> None:
    fm = fake_page_frontmatter(file=pathlib.Path(file).resolve())
    fm.config = config_test.fake_test_config()

    assert fm.get_output_path() == fm.config.output / expected


def test_page_frontmatter__get_output_path__no_config() -> None:
    fm = fake_page_frontmatter()
    with pytest.raises(ValueError, match="config must be set"):
        fm.get_output_path()


@pytest.mark.parametrize(
    ("fm_kwargs", "expected"),
    [
        (
            {"file": pathlib.Path("./pages/debug/markdown.md").resolve()},
            {
                "tags": [],
                "type": "default",
                "debug": False,
                "og": frontmatter.OpenGraphFrontmatter(
                    url="https://localhost/debug/markdown", type="website"
                ),
            },
        ),
        (
            {
                "title": "test title",
                "subtitle": None,
                "file": pathlib.Path("./pages/debug/markdown.md").resolve(),
            },
            {
                "title": "test title",
                "tags": [],
                "type": "default",
                "debug": False,
                "og": frontmatter.OpenGraphFrontmatter(
                    title="test title",
                    url="https://localhost/debug/markdown",
                    type="website",
                ),
            },
        ),
        (
            {
                "template": "props_template",
                "title": "props_title",
                "subtitle": "props_subtitle",
                "description": "props_description",
                "tags": ["tag_a", "tag_b"],
                "date": datetime.date(2022, 1, 1),
                "meta": {"foo": "bar"},
                "file": pathlib.Path("./pages/debug/markdown.md").resolve(),
                "config": config_test.fake_test_config(),
                "type": "default",
            },
            {
                "template": "props_template",
                "title": "props_title",
                "subtitle": "props_subtitle",
                "description": "props_description",
                "tags": ["tag_a", "tag_b"],
                "date": datetime.date(2022, 1, 1),
                "type": "default",
                "debug": False,
                "og": frontmatter.OpenGraphFrontmatter(
                    title="props_title",
                    description="props_subtitle",
                    url="https://localhost/debug/markdown",
                    type="website",
                ),
            },
        ),
    ],
)
def test_page_frontmatter__get_props(fm_kwargs: dict, expected: dict) -> None:
    fm = fake_page_frontmatter(**fm_kwargs)
    fm.config = config_test.fake_test_config()
    assert fm.get_props() == expected
