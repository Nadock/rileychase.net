workflow "Test, Build & Deploy" {
  on = "push"
  resolves = ["build_and_deploy_production"]
}

action "test" {
  uses = "./.actions/test"
}

action "master_filter" {
  needs = "test"
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "build_and_deploy_production" {
  needs = "master_filter"
  uses = "./.actions/build_and_deploy"
  env = {
    STAGE = "prod"
    AWS_DEFAULT_REGION = "ap-southeast-2"
  }
  secrets = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
}
