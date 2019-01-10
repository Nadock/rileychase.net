FROM amazonlinux:2

RUN yum update -y && \
	curl --silent --location https://rpm.nodesource.com/setup_10.x | bash - && \
	yum install -y make nodejs git ssh aws-cli jq
RUN npm install --global serverless gatsby-cli

WORKDIR /app
