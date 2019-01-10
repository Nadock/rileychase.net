default: test

.PHONY: deploy
deploy: install test build infra upload

.PHONY: install
install:
	cd ../rileychase.net && npm install

.PHONY: format
format: install
	cd ../rileychase.net && npm run format

.PHONY: test
test: format
	cd ../rileychase.net && npm test

.PHONY: build
build: install
	cd ../rileychase.net && npm run build

.PHONY: infra
infra:
	sls deploy

.PHONY: upload
upload:
	./bin/upload_website.sh ../rileychase.net/public

.PHONY: docker
docker: ./Dockerfile
	docker build -t nadock/rileychase.net-deploy .
	docker push nadock/rileychase.net-deploy:latest

.PHONY:
clean:
	for path in $(shell cat ../rileychase.net/.gitignore | sed "/#/d"); do rm -rf "../rileychase.net/$${path}"; done
	for path in $(shell cat ../infra/.gitignore | sed "/#/d"); do rm -rf "../infra/$${path}"; done
