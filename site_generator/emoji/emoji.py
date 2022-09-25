from .db import EMOJI

# pylint: disable=unused-argument too-many-arguments, invalid-name


def to_unicode_emoji(
    index: str,
    shortname: str,
    alias: str,
    uc: str,
    alt: str,
    title: str,
    category: str,
    options: dict,
    md,
):
    """Convert markdown emoji marker to Unicode emoji character."""
    shortname = shortname.removeprefix(":")
    shortname = shortname.removesuffix(":")
    return EMOJI[shortname]


def unicode(options, md):
    """Return the Unicode emoji DB for markdown conversion."""
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
