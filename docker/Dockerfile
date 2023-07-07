FROM python:3.11-slim as requirements-stage

RUN apt -qqy update

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.11-slim

WORKDIR /project

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN useradd -m -d /project -s /bin/bash baxa
COPY . /project
RUN chown -R baxa:baxa /project/*
RUN chmod +x /project/bin/*
ENV PATH "$PATH:/project/bin"
USER baxa
