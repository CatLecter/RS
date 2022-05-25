FROM python:3.10.4-bullseye

WORKDIR /usr/src/ugc

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
EXPOSE 8000

COPY ./requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn --bind 0.0.0.0:8000 ugc.src:app --worker-class uvicorn.workers.UvicornWorker
