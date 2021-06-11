## base image
FROM python:3.9-slim-buster AS compile-image

ARG ENV=ci

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

RUN pip install -U pipenv gunicorn

WORKDIR /code

COPY . /code/

ARG ENV=local

## add user
RUN addgroup --system pyuser && adduser --system --group pyuser
RUN chown -R pyuser:pyuser /code/ && chmod -R 755 /code/

#COPY Pipfile /code/
#COPY Pipfile.lock /code/

RUN pipenv install --system --deploy

USER pyuser

ENV ENV=${ENV}

RUN env

EXPOSE 5000

CMD ["gunicorn", "-c", "python:config.gunicorn", "app"]
