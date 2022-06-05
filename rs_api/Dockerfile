FROM python:3.10.4-bullseye

WORKDIR /usr/src/rs_api

COPY ./requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "/usr/src/rs_api/src/main.py" ]
