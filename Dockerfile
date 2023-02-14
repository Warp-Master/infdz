FROM python:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1

COPY manage.py requirements.txt /app/

WORKDIR /app
RUN pip3 install -r requirements.txt