# RileyChase.net

A [Hugo](https://gohugo.io) powered blog hosted at
[rileychase.net](https://rileychase.net) with theming based off of
[Hyde](https://themes.gohugo.io/hyde/).

## Seting up a development environment

Hugo makes life easy with their powerful CLI tool but there is still some
required configuration. In an attempt to remove even this as an issue there is
a `docker-compose` file.

### Start the development server

```bash
$> docker-compose up
```

This will start the Hugo development server and once it has started a
development copy of the webserver will be available at
[http://localhost:1313](http://localhost:1313).

### Run hugo commands

If you have the Hugo CLI installed you can freely use your native copy of the
CLI to interact with Hugo. However, if you don't have the CLI installed, you
can still use the Hugo CLI via `docker-compose`'s `run` command.

## Publishing changes

There are GitHub actions configured in the repository that will automatically
deploy any open PR to it's own testing subdomain as well as actions to publish
any new content from the `master` branch to the production website.

***TBA: Implementation details -- need to actually implement this first***
