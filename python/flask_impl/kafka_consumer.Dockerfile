FROM python:3.9-slim

WORKDIR /usr/src/app/kafka_consumer

COPY ./kafka_consumer.py .

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "kafka_consumer.py"]