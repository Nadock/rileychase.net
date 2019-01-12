FROM nadock/rileychase.net-deploy:latest

LABEL "com.github.actions.name"="Test Code"
LABEL "com.github.actions.description"="Runs unit tests and linting on code"
LABEL "com.github.actions.icon"="codepen"
LABEL "com.github.actions.color"="orange"

LABEL "repository"="https://github.com/Nadock/rileychase.net"
LABEL "homepage"="https://rileychase.net"
LABEL "maintainer"="Riley Chase <riley.chase@rileychase.net>"

ADD entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
