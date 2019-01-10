#!/usr/bin/env bash
#

# e: Exit immediately on fail
# E: Inherit ERR trap so it works correctly if something fails and we exit because of -e
# u: Treat unset variables as errors
# x: Print each instruction to stderr before executing
# o pipefail: Exit status of pipe is non-zero if any step in pipe fails
set -Eeuxo pipefail

if [[ -z "${AWS_PROFILE+x}" ]]; then
	>&2 echo "WARN: AWS_PROFILE not set, you will not be able to deploy"
	AWS_PROFILE=""
fi

docker run -it \
	-v $(pwd):/app \
	-v ~/.aws:/root/.aws \
	-e AWS_PROFILE=$AWS_PROFILE \
	-e STAGE="dev" \
	-e AWS_DEFAULT_REGION=ap-southeast-2 \
	web-deploy /bin/bash
