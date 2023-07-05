import pytest

from site_generator.emoji import emoji


@pytest.mark.parametrize(
    ["test", "expected"],
    [
        ("", ""),
        (None, None),
        ("Hello there", "Hello there"),
        (":wave:", "👋"),
        ("Hello :wave: there", "Hello 👋 there"),
        ("Hello :wave there", "Hello :wave there"),
        ("Hello :scream_cat there", "Hello :scream_cat there"),
        ("Hello :scream cat: there", "Hello :scream cat: there"),
        (":not_an_emoji:", ":not_an_emoji:"),
    ],
)
def test_replace_emoji(test, expected):
    assert emoji.replace_emoji(test) == expected
