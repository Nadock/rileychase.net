FROM nadock/rileychase.net-deploy:latest

LABEL "com.github.actions.name"="Build & Deploy"
LABEL "com.github.actions.description"="Builds a production optimised version of the website and deploys it"
LABEL "com.github.actions.icon"="cloud-lightning"
LABEL "com.github.actions.color"="orange"

LABEL "repository"="https://github.com/Nadock/rileychase.net"
LABEL "homepage"="https://rileychase.net"
LABEL "maintainer"="Riley Chase <riley.chase@rileychase.net>"

ADD entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
