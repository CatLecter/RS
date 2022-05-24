FROM python:3.10.4-bullseye

WORKDIR /usr/src/search_api

COPY ./requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "/usr/src/search_api/src/main.py" ]
