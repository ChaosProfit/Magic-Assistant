FROM nvidia/cuda:11.7.1-base-ubuntu22.04

RUN apt update -y
RUN apt install -y python3-pip
RUN apt-get -y install libpq-dev
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install poetry

ADD pyproject.toml ./pyproject.toml
ADD poetry.lock ./poetry.lock
ADD README.md ./README.md

RUN poetry config installer.max-workers 10
RUN poetry config virtualenvs.create false
RUN poetry install

ADD magic_assistant ./magic_assistant
ADD config ./config

WORKDIR ./
CMD python3 -m magic_assistant.main --io_type restful_api
