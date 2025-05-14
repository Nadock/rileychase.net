import pathlib

import pytest

from weaving import config_test, frontmatter


def fake_page_frontmatter(**kwargs) -> frontmatter.PageFrontmatter:
    if "file" not in kwargs:
        kwargs["file"] = pathlib.Path("./pages/test.md").absolute()
    return frontmatter.PageFrontmatter(**kwargs)


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
