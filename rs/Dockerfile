FROM python:3.10.4-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
EXPOSE 8000

WORKDIR /usr/src/rs

COPY ./requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD celery -A tasks worker -B --loglevel=info
