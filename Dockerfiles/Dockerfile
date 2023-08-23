FROM python:3.9-slim-bullseye

ENV http_proxy http://10.0.20.6:80
ENV https_proxy http://10.0.20.6:80

WORKDIR /web
EXPOSE 5089

COPY ./pyproject.toml /web/pyproject.toml
COPY ./.env /web/.env

RUN pip install poetry
RUN poetry install --no-root --verbose
