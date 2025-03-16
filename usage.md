# Usage Guide

This document provides instructions on how to use the [https-notif draft](https://datatracker.ietf.org/doc/draft-ietf-netconf-https-notif/) implementation in Flask and FastAPI.

## Flask Implementation

### Running the Flask Server

1. **Development Environment**:
   To run the Flask application in a development environment with SSL:

   ```bash
   flask run --host=127.0.0.1 --port=8080 --cert=../../certs/server.crt --key=../../certs/server.key
   ```

2. **Production Environment**: 
    For production, it's recommended to use Gunicorn with multiple worker nodes to handle requests efficiently:

    ```bash
    gunicorn -w 5 --certfile ../../certs/server.crt --keyfile ../../certs/server.key -b 127.0.0.1:4433 app:app
    ```

3. **Generating YANG Library for Yangson**: 
    To generate the YANG module library for Yangson:

    ```bash
    python3 mkylib.py ../../../https-notif-servers/yang_modules/
    ```

### Example of Valid JSON and XML Data

#### JSON Example:

```bash
{
    "ietf-https-notif:notification": {
        "eventTime": "2013-12-21T00:01:00Z",
        "event": {
            "event-class": "fault",
            "reporting-entity": { "card": "Ethernet0" },
            "severity": "major"
        }
    }
}
```

#### XML Example:

```bash 
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
  <eventTime>2013-12-21T00:01:00Z</eventTime>
  <event>
    <event-class>fault</event-class>
    <reporting-entity>
      <card>Ethernet0</card>
    </reporting-entity>
    <severity>major</severity>
  </event>
</notification>
```

See [this](python/flask_impl/README.md) for more information. 

## FastAPI Implementation

### Running the FastAPI Server

1. **Generate SSL Certificates**: 
    To generate self-signed certificates for the FastAPI server:

```bash
openssl req -x509 -newkey rsa:2048 -keyout keyfile.pem -out certfile.pem -days 365 -nodes
```

2. **Start the FastAPI Server**: 
    To run the FastAPI application with SSL enabled:
    ```bash
    uvicorn main:app --host 127.0.0.1 --port 8080 --ssl-keyfile ../../certs/server.key --ssl-certfile ../../certs/server.crt
    ```

### Example of Valid JSON and XML Data

#### JSON Example:

```
{    
    "ietf-https-notif:notification": {
        "eventTime": "2013-12-21T00:01:00Z",
        "event": {
            "event-class": "fault",
            "reporting-entity": { "card": "Ethernet0" },
            "severity": "major"
        }
    }
}
```

#### XML Example:

```
<notification xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
  <eventTime>2013-12-21T00:01:00Z</eventTime>
  <event>
    <event-class>fault</event-class>
    <reporting-entity>
      <card>Ethernet0</card>
    </reporting-entity>
    <severity>major</severity>
  </event>
</notification>
```
See [this](python/fast_api_impl/README.md)