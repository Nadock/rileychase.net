FROM golang:alpine

WORKDIR /app
RUN apk add --no-cache --purge hugo
CMD ["hugo", "server", "-D", "--bind", "0.0.0.0"]
