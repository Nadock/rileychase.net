workflow "Test, Build & Deploy" {
  on = "push"
  resolves = ["test_build_deploy"]
}

action "build_and_deploy_production" {
  uses = "./.actions/test_build_deploy"
  env = {
    AWS_DEFAULT_REGION = "ap-southeast-2"
  }
  secrets = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
}
