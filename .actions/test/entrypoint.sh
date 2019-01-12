#!/bin/sh
#
# GitHub Action entry point file - runs defined tests in :/infra/Makefile

# ${GITHUB_WORKSPACE} contains checked out a copy of the git commit that triggered this action
cd ${GITHUB_WORKSPACE}/infra
make test
