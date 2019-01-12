workflow "Test & Lint on Push" {
  on = "push"
  resolves = ["RUN make test"]
}

action "RUN make test" {
  uses = "./.actions/test"
}
