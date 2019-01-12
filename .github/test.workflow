workflow "Test & Lint Code" {
  on = "push"
  resolves = ["make test"]
}

action "make test" {
  uses = "./.actions/test"
}
