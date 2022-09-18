#!/usr/bin/env bash
#
# Usage: ./emoji/update.sh
#
# Update the emoji files in this repo:
#   - :/emoji/emoji.json
#   - :/pages/debug/emoji.md
#   - :/site_generator/emoji.py

if [[ ! -f "./emoji/update.sh" ]]; then
    echo 2>&1 "❌ This script must be run from the root of the repository!"
    exit 1
fi

ref=${GEMOJI_REF:-master}
curl -sSL https://raw.githubusercontent.com/github/gemoji/${ref}/db/emoji.json | jq -r tostring > ./emoji/emoji.json

pipenv run python3 ./emoji/emoji_test_gen.py ./emoji/emoji.json ./pages/debug/emoji.md
echo 2>&1 "✨ Updated ./pages/debug/emoji.md"
pipenv run python3 ./emoji/emoji_py_gen.py ./emoji/emoji.json ./site_generator/emoji.py
echo 2>&1 "✨ Updated ./site_generator/emoji.py"
