#!/usr/bin/env bash
#
# Convert gifs in a directory to webp.
#
# Usage: ./bin/convert_webp.sh [DIR]
#
# e: Exit immediately on fail
# E: Inherit ERR trap so it works correctly if something fails and we exit because of -e
# u: Treat unset variables as errors
# o pipefail: Exit status of pipe is non-zero if any step in pipe fails
set -Eeuo pipefail

for src in "${1}"/*.gif; do
    dest="${src//.gif/.webp}"
    if [[ ! -f "${dest}" ]]; then
        echo "src=${src}, dest=${dest}"
        ffmpeg -i "$src" -vcodec webp -loop 0 -pix_fmt yuva420p "${dest}"
    fi
done
