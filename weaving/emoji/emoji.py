import contextlib
from typing import Any

from .db import EMOJI


def to_unicode_emoji(
    index: str = "",
    shortname: str = "",
    alias: str = "",
    uc: str = "",
    alt: str = "",
    title: str = "",
    category: str = "",
    options: dict[Any, Any] | None = None,
    md: Any = None,
) -> str:
    """
    Convert markdown emoji marker into Unicode emoji character.

    Raises a `KeyError` if the `shortname` does not exist in the emoji DB.
    """
    del index, alias, uc, alt, title, category, options, md
    shortname = shortname.removeprefix(":")
    shortname = shortname.removesuffix(":")
    return EMOJI[shortname]


def to_markdown_db(
    options: Any, md: Any
) -> dict[str, str | dict[str, str | dict[str, str]]]:
    """Return the Unicode emoji DB in the structure required for markdown conversion."""
    del options, md
    return {
        "name": "unicode",
        "emoji": {
            f":{k}:": {
                "category": "",
                "name": k,
                "unicode": "0",
            }
            for k, v in EMOJI.items()
        },
        "aliases": {},
    }


def replace_emoji(content: str | None) -> str | None:
    """
    Find and replace any shortname emoji contents in a string with the corresponding
    Unicode emoji character.

    For example:
    >>> replace_emoji("Hello there :wave:")
    "Hello there 👋"
    """
    if not content:
        return content

    words = []
    for word in content.split(" "):
        emoji = None
        if word.startswith(":") and word.endswith(":"):
            with contextlib.suppress(KeyError):
                emoji = to_unicode_emoji(shortname=word)

        words.append(emoji or word)

    return " ".join(words)
