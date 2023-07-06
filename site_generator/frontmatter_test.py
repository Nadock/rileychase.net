import datetime
import pathlib

import pytest

from site_generator import config_test, frontmatter


def fake_page_frontmatter(**kwargs) -> frontmatter.PageFrontmatter:  # noqa: ANN003
    if "file" not in kwargs:
        kwargs["file"] = pathlib.Path("./pages/test.md").absolute()
    return frontmatter.PageFrontmatter(**kwargs)


@pytest.mark.parametrize(
    ("fm_kwargs", "cfg_kwargs", "expected"),
    [
        ({}, {}, "default.html"),
        ({"template": "foo.html"}, {}, "foo.html"),
        ({}, {"default_template": "bar.html"}, "bar.html"),
        ({"template": "foo.html"}, {"default_template": "bar.html"}, "foo.html"),
    ],
)
def test_page_frontmatter__get_template_name(fm_kwargs, cfg_kwargs, expected):
    fm = fake_page_frontmatter(**fm_kwargs)
    fm.config = config_test.fake_test_config(**cfg_kwargs)

    assert fm.get_template_name() == expected


def test_page_frontmatter__get_template_name__no_config():
    fm = fake_page_frontmatter()
    with pytest.raises(ValueError, match="config must be set"):
        fm.get_template_name()


@pytest.mark.parametrize(
    ("fm_kwargs", "cfg_kwargs", "expected"),
    [
        ({}, {}, "test.html"),
        ({"path": "foo/bar/baz.html"}, {}, "foo/bar/baz.html"),
        ({"path": "foo/bar/baz"}, {}, "foo/bar/baz/index.html"),
        ({"path": "/foo/bar/baz.html"}, {}, "foo/bar/baz.html"),
        ({"path": "/foo/bar/baz"}, {}, "foo/bar/baz/index.html"),
    ],
)
def test_page_frontmatter__get_output_path(fm_kwargs, cfg_kwargs, expected):
    fm = fake_page_frontmatter(**fm_kwargs)
    fm.config = config_test.fake_test_config(**cfg_kwargs)

    assert fm.get_output_path() == fm.config.output / expected


def test_page_frontmatter__get_output_path__no_config():
    fm = fake_page_frontmatter()
    with pytest.raises(ValueError, match="config must be set"):
        fm.get_output_path()


@pytest.mark.parametrize(
    ("fm_kwargs", "expected"),
    [
        (
            {},
            {
                "tags": [],
                "type": "default",
                "og": frontmatter.OpenGraphFrontmatter(
                    url="https://localhost/test.html", type="website"
                ),
            },
        ),
        (
            {"title": "test title", "subtitle": None},
            {
                "title": "test title",
                "tags": [],
                "type": "default",
                "og": frontmatter.OpenGraphFrontmatter(
                    title="test title",
                    url="https://localhost/test.html",
                    type="website",
                ),
            },
        ),
        (
            {
                "template": "props_template",
                "path": "props_path",
                "title": "props_title",
                "subtitle": "props_subtitle",
                "description": "props_description",
                "tags": ["tag_a", "tag_b"],
                "date": datetime.date(2022, 1, 1),
                "meta": {"foo": "bar"},
                "file": pathlib.Path("/path/to/file"),
                "config": config_test.fake_test_config(),
                "type": "default",
            },
            {
                "template": "props_template",
                "path": "props_path",
                "title": "props_title",
                "subtitle": "props_subtitle",
                "description": "props_description",
                "tags": ["tag_a", "tag_b"],
                "date": datetime.date(2022, 1, 1),
                "type": "default",
                "og": frontmatter.OpenGraphFrontmatter(
                    title="props_title",
                    description="props_subtitle",
                    url="https://localhost/props_path/",
                    type="website",
                ),
            },
        ),
    ],
)
def test_page_frontmatter__get_props(fm_kwargs, expected):
    fm = fake_page_frontmatter(**fm_kwargs)
    fm.config = config_test.fake_test_config()
    assert fm.get_props() == expected
