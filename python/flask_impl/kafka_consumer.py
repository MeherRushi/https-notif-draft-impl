from confluent_kafka import Consumer, KafkaError
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point
import json

# Kafka configuration
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "test-topic"
GROUP_ID = "influxdb-consumer-group"

consumer_config = {
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": GROUP_ID,
    "auto.offset.reset": "earliest"  
}

consumer = Consumer(consumer_config)
consumer.subscribe([KAFKA_TOPIC])

INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = ""
INFLUXDB_ORG = "NITK"
INFLUXDB_BUCKET = "test"

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
                
                event_time = data.get("ietf-https-notif:notification", {}).get("eventTime", "")
                event_class = data.get("ietf-https-notif:notification", {}).get("event", {}).get("event-class", "")
                severity = data.get("ietf-https-notif:notification", {}).get("event", {}).get("severity", "")
                reporting_entity = data.get("ietf-https-notif:notification", {}).get("event", {}).get("reporting-entity", {}).get("card", "")
                
                # Create a point for InfluxDB 
                point = (
                    Point("ietf-https-notif:notification")  
                    .tag("source", "kafka")
                    .field("event_time", event_time)
                    .field("event_class", event_class)
                    .field("severity", severity)
                    .field("reporting_entity", reporting_entity)
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
