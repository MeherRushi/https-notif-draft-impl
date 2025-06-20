from confluent_kafka import Consumer, KafkaError
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Kafka configuration
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "test-topic"
GROUP_ID = "influxdb-consumer-group"

consumer_config = {
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": GROUP_ID,
    "auto.offset.reset": "earliest"  
}

consumer = Consumer(consumer_config)
consumer.subscribe([KAFKA_TOPIC])

INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def consume_and_insert():
    print("Consuming messages from Kafka and inserting into InfluxDB...")
    try:
        while True:
            msg = consumer.poll(1.0)  # Poll Kafka for messages
            if msg is None:
                continue  # No message
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue  
                else:
                    print(f"Consumer error: {msg.error()}")
                    break
            
            # Parse the Kafka message
            message = msg.value().decode("utf-8")
            print(f"Received message: {message}")
            
            try:
                data = json.loads(message)
                
                notification_data = data.get("ietf-https-notif:notification", data.get("notification", {}))

                event_time = notification_data.get("eventTime", "")
                interface_data = str(notification_data.get("interface_data", {}))
                

                
                # Create a point for InfluxDB 
                point = (
                    Point("ietf-https-notif:notification")  
                    .tag("source", "kafka")
                    .field("event_time", event_time)
                    .field("interface_data", interface_data)
                )
                
                write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
                print(f"Inserted into InfluxDB: {data}")
            except Exception as e:
                print(f"Error processing message: {e}")
    except KeyboardInterrupt:
        print("Stopped consuming messages.")
    finally:
        consumer.close()
        client.close()

if __name__ == "__main__":
    consume_and_insert()
