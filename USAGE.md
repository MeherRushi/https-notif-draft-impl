# Usage Guide

This document provides instructions on how to use the [HTTPS Notification Draft implementation](https://datatracker.ietf.org/doc/draft-ietf-netconf-https-notif/) once it's deployed via Docker Compose.

-----

##  Running the Core Services (Collector & Publisher)

Assuming you've followed the **Installation Guide** and have your Docker Compose stack running, your **Collector** and **Publisher** applications are already active.

To ensure all services are up and running in detached mode:

```bash
docker-compose up -d
```

You can verify the status of your services at any time:

```bash
docker-compose ps
```

The `flask_collector` and `publisher_app` services should show as `Up`.

-----

## Interacting with the Collector

The Collector service (`flask_collector` or `fastapi_collector`) is designed to receive HTTPS notifications. In your Docker Compose setup, it's typically exposed on port `8080` of your host machine.

### a. Publisher Sending Data

The `publisher_app` container is configured to **automatically send interface data** to the Collector (`flask_collector:8080`) at regular intervals. This is the primary data flow.

You can monitor the logs to see the data being sent and received:

```bash
docker-compose logs -f publisher_app
docker-compose logs -f flask_collector
docker-compose logs -f kafka_consumer_app
```

### b. Manually Sending Data to the Collector (Example with `curl`)

You can also manually send JSON or XML notifications to the Collector using tools like `curl`. The Collector is typically accessible on `https://localhost:8080` from your host machine (assuming port 8080 is mapped in your `docker-compose.yml`).

Make sure your Collector is running and you have your `certs/server.crt` available.

**For JSON data:**

```bash
curl -k -X POST https://localhost:8080/relay-notification \
     -H "Content-Type: application/json" \
     -d @your_json_payload.json
```

*(Replace `your_json_payload.json` with a file containing your JSON data, or inline the JSON if it's small.)*

**For XML data:**

```bash
curl -k -X POST https://localhost:8080/relay-notification \
     -H "Content-Type: application/xml" \
     -d @your_xml_payload.xml
```

*(Replace `your_xml_payload.xml` with a file containing your XML data.)*

*The `-k` flag is used to bypass SSL certificate validation for self-signed certificates. In a production environment, you would typically configure `curl` to trust your certificate or use a valid CA-signed certificate.*

-----

## Example Valid Notification Data

Here are examples of valid JSON and XML data payloads that conform to the `ietf-https-notif` YANG model, as sent by the Publisher.

### JSON Example:

```json
{
    "ietf-https-notif:notification": {
        "eventTime": "2025-03-17T19:43:27.972894Z",
        "interface_data": {
            "interface": [
                {
                    "name": "wlp2s0",
                    "type": "1",
                    "enabled": true,
                    "admin-status": "up",
                    "oper-status": "up",
                    "if-index": 2,
                    "phys-address": "3c:91:80:2b:68:23",
                    "higher-layer-if": [],
                    "lower-layer-if": [],
                    "speed": "0",
                    "statistics": {
                        "discontinuity-time": "2025-03-17T19:43:27.952507Z",
                        "in-octets": "1592834446",
                        "in-unicast-pkts": "5375799",
                        "in-multicast-pkts": "0",
                        "in-discards": 24880,
                        "in-errors": 0,
                        "out-octets": "70768027",
                        "out-unicast-pkts": "173281",
                        "out-discards": 0,
                        "out-errors": 0
                    }
                }
            ]
        }
    }
}
```

### XML Example:

```xml
<ietf-https-notif:notification xmlns:ietf-https-notif="urn:ietf:params:xml:ns:yang:ietf-https-notif">
    <eventTime>2025-03-17T22:33:58.812159Z</eventTime>
    <interface_data>
        <interface>
            <name>wlp2s0</name>
            <type>1</type>
            <enabled>true</enabled>
            <admin-status>up</admin-status>
            <oper-status>up</oper-status>
            <if-index>2</if-index>
            <phys-address>3c:91:80:2b:68:23</phys-address>
            <speed>0</speed>
            <statistics>
                <discontinuity-time>2025-03-17T22:33:58.793164Z</discontinuity-time>
                <in-octets>2005896840</in-octets>
                <in-unicast-pkts>6749769</in-unicast-pkts>
                <in-multicast-pkts>0</in-multicast-pkts>
                <in-discards>30220</in-discards>
                <in-errors>0</in-errors>
                <out-octets>85014831</out-octets>
                <out-unicast-pkts>197084</out-unicast-pkts>
                <out-discards>0</out-discards>
                <out-errors>0</out-errors>
            </statistics>
        </interface>
    </interface_data>
</ietf-https-notif:notification>
```

-----

## 5\. Further Information

For more detailed information on specific implementations:

  * **Flask Implementation**: See the [README](https://www.google.com/search?q=python/flask_impl/README.md).
  * **FastAPI Implementation**: See the [README](https://www.google.com/search?q=python/fast_api_impl/README.md).

-----