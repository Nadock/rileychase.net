from .db import EMOJI

# pylint: disable=unused-argument too-many-arguments, invalid-name


def to_unicode_emoji(
    index: str = "",
    shortname: str = "",
    alias: str = "",
    uc: str = "",
    alt: str = "",
    title: str = "",
    category: str = "",
    options: dict | None = None,
    md=None,
) -> str:
    """
    Convert markdown emoji marker into Unicode emoji character.

    Raises a `KeyError` if the `shortname` does not exist in the emoji DB.
    """
    shortname = shortname.removeprefix(":")
    shortname = shortname.removesuffix(":")
    return EMOJI[shortname]


def to_markdown_db(options, md) -> dict:
    """Return the Unicode emoji DB in the structure required for markdown conversion."""
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
            try:
                emoji = to_unicode_emoji(shortname=word)
            except KeyError:
                pass

        words.append(emoji or word)

    return " ".join(words)
