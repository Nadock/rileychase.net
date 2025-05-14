#!/usr/bin/env bash
#
# Usage: ./update.sh
#
# Update the emoji files in this repo:
#   - :/pages/debug/emoji.md
#   - :/weaving/emoji/db.py
#   - :/weaving/emoji/emoji.json

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
OLD_DIR=$( pwd )

cd "${SCRIPT_DIR}" || exit

ref=${GEMOJI_REF:-master}
curl -sSL "https://raw.githubusercontent.com/github/gemoji/${ref}/db/emoji.json" | jq -r tostring > ./emoji.json
echo 2>&1 "✨ Updated :/weaving/emoji/emoji.json"

uv run python3 ./_generate_emoji_testpage.py ./emoji.json ../../pages/debug/emoji.md
echo 2>&1 "✨ Updated :/pages/debug/emoji.md"

uv run python3 ./_generate_emoji_db.py ./emoji.json ./db.py
echo 2>&1 "✨ Updated :/weaving/emoji/db.py"

cd "${OLD_DIR}" || exit
