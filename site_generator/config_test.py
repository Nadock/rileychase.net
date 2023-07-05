import pathlib

import pytest

from site_generator import config



def fake_test_config(**kwargs) -> config.SiteGeneratorConfig:
    if "base" not in kwargs:
        kwargs["base"] = pathlib.Path(".")
    if "templates" not in kwargs:
        kwargs["templates"] = pathlib.Path("./templates")
    if "pages" not in kwargs:
        kwargs["pages"] = pathlib.Path("./pages")
    if "static" not in kwargs:
        kwargs["static"] = pathlib.Path("./static")
    if "output" not in kwargs:
        kwargs["output"] = pathlib.Path("./output")
    return config.SiteGeneratorConfig(**kwargs)


@pytest.mark.parametrize(
    "path, expected",
    [
        (None, None),
        (pathlib.Path("."), pathlib.Path(".").absolute()),
    ],
)
def test_config__ensure_directory(path, expected):
    assert config.SiteGeneratorConfig.ensure_directory(path) == expected


@pytest.mark.parametrize(
    "base, path, expected",
    [
        (pathlib.Path("."), pathlib.Path("./test").absolute(), "./test"),
        (pathlib.Path("."), "test", "./test"),
        (pathlib.Path("."), "/usr/bin/true", "/usr/bin/true"),
    ],
)
def test_config__format_relative_path(base, path, expected):
    cfg = fake_test_config(base=base)
    assert cfg.format_relative_path(path) == expected
