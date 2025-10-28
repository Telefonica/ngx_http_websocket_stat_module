FROM python:3.12-alpine3.22

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "server.py"]
