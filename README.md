# app-cv-backend

## pre-requisites

```sh
brew install pyenv
pip3 install -U pipenv

pyenv install 3.9.1
pyenv global 3.9.1

pyenv local 3.9.1
```

### Mac OSX

```
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.zshrc

# PATH=$(pyenv root)/shims:$PATH
```

## Setup project

```sh
# To find the location of the virtual environment
pipenv --venv

# check which dependencies are mismatched
pipenv check

# see which sub-dependencies are installed by packages
pipenv graph --reverse

# installing new dependencies
pipenv install python-dotenv colorlog gunicorn
pipenv install email-listener 

# install dev dependencies for use during development
pipenv install --dev yapf
```

## Project Structure

```
.
├── Dockerfile
├── docker-composse.yml
├── .gitignore.cfg
├── .python-version
├── Makefile
├── Pipfile
├── Pipfile.lock
├── README.md
├── app
│   ├── __init__.py
├── app.py
├── config
│   ├── __init__.py
│   ├── app.default.py
│   ├── app.dev.py
│   ├── app.local.py
│   ├── app.prod.py
│   ├── credentials_decrypt.py
│   ├── crypto_secrets.json
│   ├── gunicorn.py
│   └── logger.py
├── domain
│   └── __init__.py
├── infrastructure
│   └── __init__.py
├── setup.cfg
├── shared
│   └── crypto_utils
│       ├── __init__.py
│       └── crypto_util_class.py
│       ├── crypto_util.py
├── tests
│   └── conftest.py
│   └── unit
│       └── shared_util
│           └── crypto
│               └── test_crypto_util_class.py
│               ├── test_crypto_util.py
├── test-api.sh
└── tools
    └── linter
        ├── __init__.py
        ├── lint.sh
        ├── run-mccabe.py
        ├── run-pyflakes.py
        └── utils.py
```

## Run

```sh
# set up Pipenv in your project
pipenv install

# activate the virtual environment
pipenv shell

# launch the app 
ENV=ci flask run
ENV=ci gunicorn --reload --config config/gunicorn.conf.py app:run
```

## Deploy

```sh
# Deploying
pipenv install --deploy
```