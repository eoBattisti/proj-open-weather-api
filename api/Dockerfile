FROM python:3.12.4-slim-bullseye

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install system dependencies
RUN apt update && apt install -y --no-install-recommends \
    build-essential postgresql postgresql-contrib libpq-dev python3-dev 

ARG MODE

WORKDIR $HOME/app

COPY . .

ENV MODE=${MODE}

RUN ./docker/build.sh 

EXPOSE $PORT
