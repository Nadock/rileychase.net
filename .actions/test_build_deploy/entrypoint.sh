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
BRANCH_NAME=$(git branch | grep \* | cut -d " " -f2)

if [[ ${BRANCH_NAME} == "master" ]]; then
	STAGE=prod
	make deploy
elif [[ ${BRANCH_NAME} == "dev" ]]; then
	STAGE=dev
	# TODO: configure a development environment
	# make deploy
	make test
else
	make test
fi
