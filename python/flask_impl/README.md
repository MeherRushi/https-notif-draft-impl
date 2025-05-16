# Flask Implementation

- Flask is based on WSGI based implemenation
- So here we can use any standard webserver with the application server addition (werkzeug library)[https://stackoverflow.com/questions/37004983/what-exactly-is-werkzeug]

- synchronously handles requests but we can set the number of worker nodes

- Here, we enable SSL using self signed certificates while `    app.run(ssl_context='adhoc') ` and `--cert=adhoc` flag

- We can also generate a certificate using openssl and then use them as mentioned in the reference links (https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)

```bash
pip install requirements.txt
```

- dev
```bash
flask run --host=0.0.0.0 --port=8080 --cert=../../certs/server.crt --key=../../certs/server.key
```

- prod
```bash
gunicorn -w 5 --certfile ../../certs/server.crt --keyfile ../../certs/server.key -b 127.0.0.1:4433 app:app
```

- generating the library yang file for yangson

```bash
python3 mkylib.py ../../../https-notif-servers/yang_modules/
```
```
{
  "ietf-yang-library:modules-state": {
    "module-set-id": "",
    "module": [
      {
        "name": "ietf-https-notif",
        "revision": "",
        "namespace": "urn:ietf:params:xml:ns:netconf:notification:1.0",
        "conformance-type": "implement"
      },
      {
        "name": "ietf-yang-types",
        "revision": "2013-07-15",
        "namespace": "urn:ietf:params:xml:ns:yang:ietf-yang-types",
        "conformance-type": "import"
      }
    ]
  }
}
```

Eg for valid json data

```
{
    "ietf-https-notif:notification": {
        "eventTime": "2025-03-17T19:43:27.972894Z",
        "interface_data": {
            "interface": [
                {
                    "name": "wlp2s0",
                    "description": "",
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
                },
                {
                    "name": "br-910b760a58dc",
                    "description": "",
                    "type": "1",
                    "enabled": false,
                    "admin-status": "down",
                    "oper-status": "down",
                    "if-index": 3,
                    "phys-address": "02:42:c0:33:32:37",
                    "higher-layer-if": [],
                    "lower-layer-if": [],
                    "speed": "0",
                    "statistics": {
                        "discontinuity-time": "2025-03-17T19:43:27.955690Z",
                        "in-octets": "0",
                        "in-unicast-pkts": "0",
                        "in-multicast-pkts": "0",
                        "in-discards": 0,
                        "in-errors": 0,
                        "out-octets": "0",
                        "out-unicast-pkts": "0",
                        "out-discards": 0,
                        "out-errors": 0
                    }
                },
                {
                    "name": "br0",
                    "description": "",
                    "type": "1",
                    "enabled": true,
                    "admin-status": "up",
                    "oper-status": "up",
                    "if-index": 5,
                    "phys-address": "da:4a:7d:24:dd:33",
                    "higher-layer-if": [],
                    "lower-layer-if": [],
                    "speed": "0",
                    "statistics": {
                        "discontinuity-time": "2025-03-17T19:43:27.958623Z",
                        "in-octets": "2012",
                        "in-unicast-pkts": "33",
                        "in-multicast-pkts": "32",
                        "in-discards": 0,
                        "in-errors": 0,
                        "out-octets": "6068",
                        "out-unicast-pkts": "52",
                        "out-discards": 0,
                        "out-errors": 0
                    }
                },
                {
                    "name": "docker0",
                    "description": "",
                    "type": "1",
                    "enabled": false,
                    "admin-status": "down",
                    "oper-status": "down",
                    "if-index": 4,
                    "phys-address": "02:42:05:83:6b:7b",
                    "higher-layer-if": [],
                    "lower-layer-if": [],
                    "speed": "0",
                    "statistics": {
                        "discontinuity-time": "2025-03-17T19:43:27.962795Z",
                        "in-octets": "0",
                        "in-unicast-pkts": "0",
                        "in-multicast-pkts": "0",
                        "in-discards": 0,
                        "in-errors": 0,
                        "out-octets": "0",
                        "out-unicast-pkts": "0",
                        "out-discards": 0,
                        "out-errors": 0
                    }
                },
                {
                    "name": "lo",
                    "description": "",
                    "type": "772",
                    "enabled": true,
                    "admin-status": "testing",
                    "oper-status": "unknown",
                    "if-index": 1,
                    "phys-address": "00:00:00:00:00:00",
                    "higher-layer-if": [],
                    "lower-layer-if": [],
                    "speed": "0",
                    "statistics": {
                        "discontinuity-time": "2025-03-17T19:43:27.965362Z",
                        "in-octets": "10222658",
                        "in-unicast-pkts": "52836",
                        "in-multicast-pkts": "0",
                        "in-discards": 0,
                        "in-errors": 0,
                        "out-octets": "10222658",
                        "out-unicast-pkts": "52836",
                        "out-discards": 0,
                        "out-errors": 0
                    }
                },
                {
                    "name": "veth3",
                    "description": "",
                    "type": "1",
                    "enabled": true,
                    "admin-status": "up",
                    "oper-status": "up",
                    "if-index": 8,
                    "phys-address": "5a:07:2b:6c:20:de",
                    "higher-layer-if": [],
                    "lower-layer-if": [],
                    "speed": "0",
                    "statistics": {
                        "discontinuity-time": "2025-03-17T19:43:27.968879Z",
                        "in-octets": "393086799",
                        "in-unicast-pkts": "2447215",
                        "in-multicast-pkts": "0",
                        "in-discards": 0,
                        "in-errors": 0,
                        "out-octets": "454073677",
                        "out-unicast-pkts": "2470847",
                        "out-discards": 0,
                        "out-errors": 0
                    }
                },
                {
                    "name": "veth1",
                    "description": "",
                    "type": "1",
                    "enabled": true,
                    "admin-status": "up",
                    "oper-status": "up",
                    "if-index": 6,
                    "phys-address": "12:43:1b:3f:fe:8d",
                    "higher-layer-if": [],
                    "lower-layer-if": [],
                    "speed": "0",
                    "statistics": {
                        "discontinuity-time": "2025-03-17T19:43:27.972562Z",
                        "in-octets": "454063742",
                        "in-unicast-pkts": "2470760",
                        "in-multicast-pkts": "0",
                        "in-discards": 0,
                        "in-errors": 0,
                        "out-octets": "393096934",
                        "out-unicast-pkts": "2447304",
                        "out-discards": 0,
                        "out-errors": 0
                    }
                }
            ]
        }
    }
}
```

Eg for valid xml data

```
<ietf-https-notif:notification>
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
		<interface>
			<name>br-910b760a58dc</name>
			<type>1</type>
			<enabled>false</enabled>
			<admin-status>down</admin-status>
			<oper-status>down</oper-status>
			<if-index>3</if-index>
			<phys-address>02:42:c0:33:32:37</phys-address>
			<speed>0</speed>
			<statistics>
				<discontinuity-time>2025-03-17T22:33:58.798027Z</discontinuity-time>
				<in-octets>0</in-octets>
				<in-unicast-pkts>0</in-unicast-pkts>
				<in-multicast-pkts>0</in-multicast-pkts>
				<in-discards>0</in-discards>
				<in-errors>0</in-errors>
				<out-octets>0</out-octets>
				<out-unicast-pkts>0</out-unicast-pkts>
				<out-discards>0</out-discards>
				<out-errors>0</out-errors>
			</statistics>
		</interface>
		<interface>
			<name>br0</name>
			<type>1</type>
			<enabled>true</enabled>
			<admin-status>up</admin-status>
			<oper-status>up</oper-status>
			<if-index>5</if-index>
			<phys-address>da:4a:7d:24:dd:33</phys-address>
			<speed>0</speed>
			<statistics>
				<discontinuity-time>2025-03-17T22:33:58.800636Z</discontinuity-time>
				<in-octets>2124</in-octets>
				<in-unicast-pkts>35</in-unicast-pkts>
				<in-multicast-pkts>34</in-multicast-pkts>
				<in-discards>0</in-discards>
				<in-errors>0</in-errors>
				<out-octets>8844</out-octets>
				<out-unicast-pkts>77</out-unicast-pkts>
				<out-discards>0</out-discards>
				<out-errors>0</out-errors>
			</statistics>
		</interface>
		<interface>
			<name>docker0</name>
			<type>1</type>
			<enabled>false</enabled>
			<admin-status>down</admin-status>
			<oper-status>down</oper-status>
			<if-index>4</if-index>
			<phys-address>02:42:05:83:6b:7b</phys-address>
			<speed>0</speed>
			<statistics>
				<discontinuity-time>2025-03-17T22:33:58.803211Z</discontinuity-time>
				<in-octets>0</in-octets>
				<in-unicast-pkts>0</in-unicast-pkts>
				<in-multicast-pkts>0</in-multicast-pkts>
				<in-discards>0</in-discards>
				<in-errors>0</in-errors>
				<out-octets>0</out-octets>
				<out-unicast-pkts>0</out-unicast-pkts>
				<out-discards>0</out-discards>
				<out-errors>0</out-errors>
			</statistics>
		</interface>
		<interface>
			<name>lo</name>
			<type>772</type>
			<enabled>true</enabled>
			<admin-status>testing</admin-status>
			<oper-status>unknown</oper-status>
			<if-index>1</if-index>
			<phys-address>00:00:00:00:00:00</phys-address>
			<speed>0</speed>
			<statistics>
				<discontinuity-time>2025-03-17T22:33:58.805633Z</discontinuity-time>
				<in-octets>12209653</in-octets>
				<in-unicast-pkts>62427</in-unicast-pkts>
				<in-multicast-pkts>0</in-multicast-pkts>
				<in-discards>0</in-discards>
				<in-errors>0</in-errors>
				<out-octets>12209653</out-octets>
				<out-unicast-pkts>62427</out-unicast-pkts>
				<out-discards>0</out-discards>
				<out-errors>0</out-errors>
			</statistics>
		</interface>
		<interface>
			<name>veth3</name>
			<type>1</type>
			<enabled>true</enabled>
			<admin-status>up</admin-status>
			<oper-status>up</oper-status>
			<if-index>8</if-index>
			<phys-address>5a:07:2b:6c:20:de</phys-address>
			<speed>0</speed>
			<statistics>
				<discontinuity-time>2025-03-17T22:33:58.808447Z</discontinuity-time>
				<in-octets>463649916</in-octets>
				<in-unicast-pkts>3629306</in-unicast-pkts>
				<in-multicast-pkts>0</in-multicast-pkts>
				<in-discards>0</in-discards>
				<in-errors>0</in-errors>
				<out-octets>554947705</out-octets>
				<out-unicast-pkts>3664665</out-unicast-pkts>
				<out-discards>0</out-discards>
				<out-errors>0</out-errors>
			</statistics>
		</interface>
		<interface>
			<name>veth1</name>
			<type>1</type>
			<enabled>true</enabled>
			<admin-status>up</admin-status>
			<oper-status>up</oper-status>
			<if-index>6</if-index>
			<phys-address>12:43:1b:3f:fe:8d</phys-address>
			<speed>0</speed>
			<statistics>
				<discontinuity-time>2025-03-17T22:33:58.811861Z</discontinuity-time>
				<in-octets>554933451</in-octets>
				<in-unicast-pkts>3664540</in-unicast-pkts>
				<in-multicast-pkts>0</in-multicast-pkts>
				<in-discards>0</in-discards>
				<in-errors>0</in-errors>
				<out-octets>463664370</out-octets>
				<out-unicast-pkts>3629433</out-unicast-pkts>
				<out-discards>0</out-discards>
				<out-errors>0</out-errors>
			</statistics>
		</interface>
	</interface_data>
</ietf-https-notif:notification>
```

---

## Setting up Kafka and InfluxDB 

1. Run the following command to set up InfluxDB using Docker Compose:

```bash
docker-compose up -d
```

2. Go to `localhost:8086` in your browser and sign up. 
   
3. Copy the `operator API token`, `Org` and `Bucket` and add it to the `.env` file.

4. Run the `kafka_consumer.py` in the background. 

5. Send some relay-notifications to the collector 

6. To query the tsdb run `read_db.py`



