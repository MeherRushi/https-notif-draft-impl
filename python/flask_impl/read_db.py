from influxdb_client import InfluxDBClient

url = "http://localhost:8086"
token = ""
org = "NITK"

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
