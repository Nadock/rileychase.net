#!/usr/bin/env python
"""
Generator script that generates ./pages/emoji_test.md from a gemoji source JSON file.
"""

import json
import pathlib
import sys


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "usage: emoji_test_gen.py [gemoji_json_path] [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    src = pathlib.Path(sys.argv[1])
    dest = pathlib.Path(sys.argv[2])

    # Example emoji_db element
    # {
    #     "emoji": "😀",
    #     "description": "grinning face",
    #     "category": "Smileys & Emotion",
    #     "aliases": ["grinning"],
    #     "tags": ["smile", "happy"],
    #     "unicode_version": "6.1",
    #     "ios_version": "6.0",
    # },
    emoji_db = json.loads(src.read_text("utf-8"))

    lines = [
        "---",
        "title: Emoji Test",
        "subtitle: A test of all available emojis",
        "description: Emoji test",
        "---",
        "",
        "## Emoji",
        "",
        "| GemEmoji | Rendered | Aliases |",
        "| :------: | :------: | ------- |",
    ]

    for emoji_record in emoji_db:
        emoji = emoji_record["emoji"]
        rendered = f":{emoji_record['aliases'][0]}:"
        aliases = ", ".join([f"`:{a}:`" for a in emoji_record["aliases"]])
        lines.append(f"| {emoji} | {rendered} | {aliases} |")

    lines.append("")

    dest.write_text("\n".join(lines), "utf-8")


if __name__ == "__main__":
    main()
