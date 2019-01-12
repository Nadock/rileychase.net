#!/bin/sh
#
# GitHub Action entry point file - runs defined tests in :/infra/Makefile

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
