FROM python:3.12.4-slim-bullseye

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


RUN apt update

WORKDIR /usr/src/app

COPY ./requirements/main.txt ./

RUN pip install --no-cache-dir -r main.txt

COPY . .
