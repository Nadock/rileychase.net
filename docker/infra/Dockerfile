FROM amazonlinux:2

RUN curl --silent --location https://rpm.nodesource.com/setup_10.x | bash - \
    && yum install -y nodejs \
    && yum update -y \
    && npm install --global serverless

WORKDIR /app

