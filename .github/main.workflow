workflow "Test, Build & Deploy" {
	on = "push"
	resolves = ["build_and_test"]
}

action "test" {
	uses = "./.actions/test"
}

action "build_and_test" {
	needs = "test"
	needs = "master_filter"
	uses ="./.actions/build_and_test"
}

action "master_filter" {
	uses = "actions/bin/filter@master"
	args = "branch master"
}
