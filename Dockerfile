FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

COPY ./requirements.txt /workspace/

RUN pip install --upgrade pip \
    && pip install --force-reinstall -r /workspace/requirements.txt