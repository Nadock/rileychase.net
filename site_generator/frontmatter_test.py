import pathlib

import pytest

from site_generator import config_test, frontmatter

# pylint: disable=missing-function-docstring, invalid-name


def fake_page_frontmatter(**kwargs) -> frontmatter.PageFrontmatter:
    if "file" not in kwargs:
        kwargs["file"] = pathlib.Path("./pages/test.md").absolute()
    return frontmatter.PageFrontmatter(**kwargs)


@pytest.mark.parametrize(
    "fm_kwargs, cfg_kwargs ,expected",
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
    with pytest.raises(ValueError):
        fm = fake_page_frontmatter()
        fm.get_template_name()


@pytest.mark.parametrize(
    "fm_kwargs, cfg_kwargs ,expected",
    [
        ({}, {}, "test.html"),
        ({"path": "foo/bar/baz.html"}, {}, "foo/bar/baz.html"),
        ({"path": "foo/bar/baz"}, {}, "foo/bar/baz/index.html"),
    ],
)
def test_page_frontmatter__get_output_path(fm_kwargs, cfg_kwargs, expected):
    fm = fake_page_frontmatter(**fm_kwargs)
    fm.config = config_test.fake_test_config(**cfg_kwargs)

    assert fm.get_output_path() == fm.config.output / expected


def test_page_frontmatter__get_output_path__no_config():
    with pytest.raises(ValueError):
        fm = fake_page_frontmatter()
        fm.get_output_path()
