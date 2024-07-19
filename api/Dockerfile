FROM python:3.12.4-slim-bullseye

# Install system dependencies
RUN apt update && apt install -y --no-install-recommends \
    build-essential postgresql postgresql-contrib libpq-dev python3-dev 


WORKDIR $HOME/app

COPY . .

RUN ./docker/build.sh 

EXPOSE $PORT

ENTRYPOINT ["./docker/entrypoint.sh"]
