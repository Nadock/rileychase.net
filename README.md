# rileychase.net

Simple static site generator and content that powers [rileychase.net](https://rileychase.net).

[![Deploy Website](https://github.com/Nadock/rileychase.net/actions/workflows/deploy_website.yml/badge.svg)](https://github.com/Nadock/rileychase.net/actions/workflows/deploy_website.yml)

## To do

Before this is "done" and ready for regular use, we still need to do the following:

- [x] Fix code block layout - currently copies from `<table>` elements
- [x] Setup colour scheme and apply to headers, links, tables, etc
- [x] Decide on primary highlight colour (ie: everything that's currently `orange`)
- [x] Consider font choice - see if we can use Fira Code as our mono spaced font with ligature support
- [x] Decide on inital set of required post metadata
- [x] Footer with copywrite and links
- [x] Make links not ending in `.html` work
- [x] 404 page
- ~~[ ] Docker things~~
- [ ] AWS infra
  - [x] CF Distro & S3
  - [ ] ACM cert
  - [ ] DNS config
- [ ] Home page content
  - [ ] No JS
  - [ ] Social links
- [ ] Light mode / dark mode toggle
~~- [ ] Nav menu animation improvement~~
- [x] Consistent site header with nav links
- [ ] Tags support (view list, jump to page)
- [ ] Blog support (view list)
- [x] CI Workflows
  - [x] Code quality checks on PR
  - [x] Markdown lint on PR
  ~~- [ ] Deploy site CFN on change~~
  - [x] Sync site contents & invalidate on change
- [ ] New README and content
