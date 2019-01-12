workflow "Test, Build & Deploy" {
	on = "push"
	resolves = ["build_and_test"]
}

action "test" {
	uses = "./.actions/test"
}

action "master_filter" {
	needs = "test"
	uses = "actions/bin/filter@master"
	args = "branch master"
}

action "build_and_deploy" {
	needs = "master_filter"
	uses ="./.actions/build_and_deploy"
}
