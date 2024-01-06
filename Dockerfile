FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y libpq-dev gcc git

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app
EXPOSE 8000