FROM python:3.9-slim

WORKDIR /app

COPY . /app

WORKDIR /app/python/flask_impl

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080", "--cert=../../certs/server.crt", "--key=../../certs/server.key"]


