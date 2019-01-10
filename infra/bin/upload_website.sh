#!/usr/bin/env bash
#
# Uploads contents of directory name in AWS CF stack output
#
# Usage: upload_website [path_to_dir]

# e: Exit immediately on fail
# E: Inherit ERR trap so it works correctly if something fails and we exit because of -e
# u: Treat unset variables as errors
# x: Print each instruction to stderr before executing
# o pipefail: Exit status of pipe is non-zero if any step in pipe fails
set -Eeuxo pipefail

if [[ -z "${1}+x" ]]; then
	>&2 echo "Usage: upload_website [path_to_dir]"
	exit 1
fi

path=${1}
bucket_name=$(aws cloudformation describe-stacks --stack-name "rileychase-net-$STAGE" | \
			  jq '.Stacks[0].Outputs[] | select(.OutputKey == "WebsiteBucketOutput") | .OutputValue' | \
			  sed -e 's/^"//' -e 's/"$//')

>&2 echo "upload ${path} to s3://${bucket_name}"
aws s3 sync "${path}" "s3://${bucket_name}"
