FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /pokesearch

WORKDIR /pokesearch

COPY requirements.txt /pokesearch

RUN pip install --no-cache-dir -r requirements.txt --user

COPY . /pokesearch

RUN python manage.py migrate

RUN python manage.py collectstatic --noinput