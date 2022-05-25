FROM python:3.10.4-bullseye

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY auth_api/ auth_api/

EXPOSE 5000
