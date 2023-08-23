FROM python:3.9-slim-bullseye

ENV http_proxy http://10.0.20.6:80
ENV https_proxy http://10.0.20.6:80

WORKDIR /web

RUN mkdir -p /opt/oracle
COPY ./poetry.lock /web/poetry.lock
COPY ./pyproject.toml /web/pyproject.toml
COPY ./.env /web/.env
COPY ./instantclient-basic-linux.x64-21.11.0.0.0dbru.zip /opt/oracle/instantclient-basic-linux.x64-21.11.0.0.0dbru.zip

RUN apt-get update
RUN apt-get install libaio1 unzip
RUN unzip /opt/oracle/instantclient-basic-linux.x64-21.11.0.0.0dbru.zip -d /opt/oracle
RUN pip install poetry
RUN poetry install --no-root
