#!/usr/bin/env bash
#
# GitHub Action entry point
#
# On `*` branches, run tests.
# On `dev` branch, run development environment deploy
# On `master` branch, run production environment deploy


# e: Exit immediately on fail
# E: Inherit ERR trap so it works correctly if something fails and we exit because of -e
# u: Treat unset variables as errors
# x: Print each instruction to stderr before executing
# o pipefail: Exit status of pipe is non-zero if any step in pipe fails
set -Eeuxo pipefail

# ${GITHUB_WORKSPACE} contains checked out a copy of the git commit that triggered this action
cd ${GITHUB_WORKSPACE}/infra
BRANCH_NAME=$(echo ${GITHUB_REF} | cut -d "/" -f3)

if [[ ${BRANCH_NAME} == "master" ]]; then
	export STAGE=prod
	make deploy
elif [[ ${BRANCH_NAME} == "dev" ]]; then
	export STAGE=dev
	make deploy
else
	make test
fi
