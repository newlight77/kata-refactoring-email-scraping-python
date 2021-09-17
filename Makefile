#!make

# Makefile for Demo Auth Serve
SHELL := /bin/sh

export ENV ?= local
#export BUILD = $(shell git describe --always)-$(shell date +%Y%m%d%H%M%S)
#export TAG = $(shell git describe --abbrev=0 --tags)
#BRANCH = $(shell git branch --show-current)
export VERSION ?= $(shell git describe --always)

$(info version = $(VERSION))
$(info env = $(ENV))

install:
	#@pyenv install 3.9.1
	@pyenv local 3.9.1
	@pipenv install
	@pipenv shell

lint:
	@./tools/linter/lint.sh

test:
	@PYTHONPATH=. pytest -v -s

test-key:
	@PYTHONPATH=. pytest -v -s -k $(key)

test-unit:
	@PYTHONPATH=. pytest -v -s -k unit

test-component:
	@PYTHONPATH=. pytest -v -s -k component

test-hexagonal:
	@PYTHONPATH=. pytest -v -s -m "hexagonal"

test-pipe:
	@PYTHONPATH=. pytest -v -s -m "pipe"

test-shared:
	@PYTHONPATH=. pytest -v -s -m "shared"

run:
	@python app.py

run-g:
	@gunicorn --config ./config/gunicorn.py "app"

run-local:
	@ENV=local python app.py

run-dev:
	
	@ENV=dev python app.py

dc-build:
	@docker build . -t app-cv-backend:dev --build-arg ENV=$(ENV)

dc-run:
	@docker run -it -p 5000:5000 --env ENV=$(ENV) app-cv-backend:ci

dc-push:
	@docker-compose push app-cv-backend

dc-up:
	@docker-compose up -d
