FROM python:3.12-alpine3.22

WORKDIR /app

ADD . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "server.py"]
