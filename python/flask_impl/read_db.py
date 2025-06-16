from influxdb_client import InfluxDBClient
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

url = "http://localhost:8086"
token = os.getenv("INFLUXDB_TOKEN")
org = os.getenv("INFLUXDB_ORG")

client = InfluxDBClient(url=url, token=token, org=org)

query_api = client.query_api()

query = """
from(bucket: "test")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "ietf-https-notif:notification")
  |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn: "_value")
"""

tables = query_api.query(query)

for table in tables:
    for record in table.records:
        print(record)
        print('----------------------------------------------------------------------------------------------------------------------')
