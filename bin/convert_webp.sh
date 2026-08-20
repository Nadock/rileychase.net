#!/usr/bin/env bash
#
# Convert gifs in a directory to webp.
#
# Usage: ./bin/.sh [DIR]
#
# e: Exit immediately on fail
# E: Inherit ERR trap so it works correctly if something fails and we exit because of -e
# u: Treat unset variables as errors
# o pipefail: Exit status of pipe is non-zero if any step in pipe fails
set -Eeuo pipefail

for src in "${1}"/*.jpg; do
    dest="${src//.jpg/.webp}"
    if [[ ! -f "${dest}" && -f "${src}" ]]; then
        echo "src=${src}, dest=${dest}"
        ffmpeg -i "$src" -vcodec webp -loop 0 "${dest}"
    fi
done

for src in "${1}"/*.png; do
    dest="${src//.png/.webp}"
    if [[ ! -f "${dest}" && -f "${src}" ]]; then
        echo "src=${src}, dest=${dest}"
        ffmpeg -i "$src" -vcodec webp -loop 0 "${dest}"
    fi
done

for src in "${1}"/*.gif; do
    dest="${src//.gif/.webp}"
    if [[ ! -f "${dest}" && -f "${src}" ]]; then
        echo "src=${src}, dest=${dest}"
        ffmpeg -i "$src" -vcodec webp -loop 0 "${dest}"
    fi
done
