from flask import Flask, request, jsonify, Response
from prometheus_client import Counter, Gauge, generate_latest 
import json
import xmltodict
import cbor2
import re
from http import HTTPStatus
from yangson import DataModel
from yangson.enumerations import ContentType
import time
from confluent_kafka import Producer


# Kafka producer configuration
KAFKA_TOPIC_NAME = 'test-topic'
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def delivery_report(err, msg):
    if err:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# Define constants for the URNs, namespace, and JSON keys
URN_ENCODING_JSON = "urn:ietf:capability:https-notif-receiver:encoding:json"
URN_ENCODING_XML = "urn:ietf:capability:https-notif-receiver:encoding:xml"
URN_ENCODING_CBOR = "urn:ietf:capability:https-notif-receiver:encoding:cbor"
JSON_RECEIVER_CAPABILITIES = "receiver-capabilities"
JSON_RECEIVER_CAPABILITY = "receiver-capability"
UHTTPS_CONTENT_TYPE = 'Content-Type'
UHTTPS_ACCEPT = 'Accept'

# Define constants for media types
MIME_APPLICATION_XML = "application/xml"
MIME_APPLICATION_JSON = "application/json"
MIME_APPLICATION_CBOR = "application/cbor"  #Unsure about its existence.

# collector capabilities
json_capable = True
xml_capable = True
cbor_capable = True

# Define your YANG module path and model name
yang_dir_path = "../../yang_modules/"
yang_library_path = "../../yang_modules/yang-library.json"

app = Flask(__name__)

# Initialize the YANG data model
data_model = DataModel.from_file(yang_library_path, [yang_dir_path])

# Custom function to remove namespaces from XML keys
def strip_namespace(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            stripped_key = key.split(':')[-1] if ':' in key else key
            new_data[stripped_key] = strip_namespace(value)
        return new_data
    elif isinstance(data, list):
        return [strip_namespace(item) for item in data]
    else:
        return data

def validate_relay_notif(data_string):
    req_content_type = request.headers.get(UHTTPS_CONTENT_TYPE)
    try:
        if req_content_type == MIME_APPLICATION_JSON:
            json_data = json.loads(data_string)
        elif req_content_type == MIME_APPLICATION_XML:
            parsed_xml = xmltodict.parse(data_string, process_namespaces=False)
            json_data = parsed_xml
            list_of_interfaces = json_data['ietf-https-notif:notification']['interface_data']['interface']
            
            # Ensure it's always a list
            if isinstance(list_of_interfaces, dict):
                list_of_interfaces = [list_of_interfaces]
            
            # Process each interface in the list
            for interface in list_of_interfaces:
                # Convert 'enabled' to boolean
                interface['enabled'] = interface['enabled'] != 'false'
                
                # Convert 'if-index' to int
                if isinstance(interface.get('if-index'), str):
                    interface['if-index'] = int(interface['if-index'])
                
                # Convert statistics values to int
                stats_keys = ['in-discards', 'in-errors', 'in-unknown-protos', 'out-discards', 'out-errors']
                if 'statistics' in interface:
                    for key in stats_keys:
                        if key in interface['statistics'] and isinstance(interface['statistics'][key], str):
                            interface['statistics'][key] = int(interface['statistics'][key])
            
            # Assign the updated list back to JSON structure
            json_data['ietf-https-notif:notification']['interface_data']['interface'] = list_of_interfaces

        elif req_content_type == MIME_APPLICATION_CBOR:    
            parsed_cbor = bytes.fromhex(data_string.decode('utf-8'))
            json_data = cbor2.loads(parsed_cbor)
        else:
            return 0, "Invalid Content-Type"

    except Exception as e:
        app.logger.error(f"Parsing error: {e}")
        return 0, "Parsing error: invalid data format"

    try:
        instance = data_model.from_raw(json_data)
        instance.validate(ctype=ContentType.all)
        return 1, None
    except Exception as e:
        app.logger.error(f"Validation error: {e}")
        return 0, "Validation error: data does not conform to the YANG module"


def build_capabilities_data(json_capable, xml_capable, cbor_capable):
    capabilities_data = []
    if json_capable:
        capabilities_data.append(URN_ENCODING_JSON)
    if xml_capable:
        capabilities_data.append(URN_ENCODING_XML)
    if cbor_capable:
        capabilities_data.append(URN_ENCODING_CBOR)
    return capabilities_data

def build_xml(capabilities_data):
    """Builds an XML string from capabilities data."""
    xml_content = '<receiver-capabilities>'
    for capability in capabilities_data:
        xml_content += f'    <receiver-capability>{capability}</receiver-capability>\n'
    xml_content += '</receiver-capabilities>'
    return xml_content

def build_json(capabilities_data):
    """Builds a JSON structure from capabilities data."""
    return json.dumps({
        JSON_RECEIVER_CAPABILITIES: {
            JSON_RECEIVER_CAPABILITY: capabilities_data
        }
    }, indent=2)

def build_cbor(capabilities_data):
    """Builds a CBOR structure from capabilities data."""
    data =  cbor2.dumps({
        JSON_RECEIVER_CAPABILITIES: {
            JSON_RECEIVER_CAPABILITY: capabilities_data
        }
    }).hex()

    return data

def get_q_value(accept_header, media_type):
    """Extracts the q value for a specific media type from the Accept header."""
    pattern = re.compile(rf"{media_type}(;q=([0-9.]+))?")
    match = pattern.search(accept_header)
    if match:
        q_value = match.group(2)
        return float(q_value) if q_value else 1.0
    return 0.0

def get_default_response(json_capable, xml_capable, cbor_capable, capabilities_data):
    """Returns the default response based on capabilities."""
    if xml_capable:
        return build_xml(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_XML}
    elif json_capable:
        return build_json(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_JSON}
    elif cbor_capable:
        return build_cbor(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_CBOR}
    return jsonify({"error": "No valid capabilities found"}), HTTPStatus.INTERNAL_SERVER_ERROR

def respond_with_content_type(accept_header, json_capable, xml_capable, cbor_capable, capabilities_data):
    """Responds based on the Accept header and content capabilities, considering q-values."""
    q_xml = get_q_value(accept_header, MIME_APPLICATION_XML)
    q_json = get_q_value(accept_header, MIME_APPLICATION_JSON)
    q_cbor = get_q_value(accept_header, MIME_APPLICATION_CBOR)

    if q_xml < 0 or q_json < 0 or q_cbor < 0 or q_xml > 1 or q_json > 1 or q_cbor > 1:
        return jsonify({"error": "Invalid q value"}), HTTPStatus.BAD_REQUEST

    if q_json == 0 and q_xml == 0 and q_cbor == 0:
        return get_default_response(json_capable, xml_capable, cbor_capable, capabilities_data)

    # if xml_capable and (q_xml >= q_json or not json_capable):
    if(xml_capable and (q_xml >= q_json and q_xml >= q_cbor)):
        return build_xml(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_XML}
    
    q_max = max(q_xml,q_json,q_cbor)
    if q_max == q_xml and xml_capable:
        return build_xml(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_XML}
    elif q_max == q_json and json_capable:
        return build_json(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_JSON}
    elif q_max == q_cbor and cbor_capable:
        return build_cbor(capabilities_data), HTTPStatus.OK, {'Content-Type': MIME_APPLICATION_CBOR}

    return jsonify({"error": "Not acceptable"}), HTTPStatus.NOT_ACCEPTABLE

@app.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Handles the /capabilities GET request."""
    capabilities_data = build_capabilities_data(json_capable, xml_capable, cbor_capable)
    print(capabilities_data)

    accept_header = request.headers.get(UHTTPS_ACCEPT)
    print(accept_header)
    if accept_header:
        return respond_with_content_type(accept_header, json_capable, xml_capable, cbor_capable, capabilities_data)

    return get_default_response(json_capable, xml_capable, cbor_capable, capabilities_data)

@app.route('/relay-notification', methods=['POST'])
def post_notification():
    print(f"Received notification at {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}.{int(time.time() * 1000) % 1000:03d}")
    req_content_type = request.headers.get(UHTTPS_CONTENT_TYPE)

    if req_content_type is None:
        return "Content-type is None -> Empty Body Notification", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    if req_content_type not in [MIME_APPLICATION_JSON, MIME_APPLICATION_XML, MIME_APPLICATION_CBOR]:
        return "Unsupported Media Type", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    if (req_content_type == MIME_APPLICATION_JSON and not json_capable) or \
       (req_content_type == MIME_APPLICATION_XML and not xml_capable) or \
        (req_content_type == MIME_APPLICATION_CBOR and not cbor_capable):
        return f"{req_content_type} encoding not supported", HTTPStatus.UNSUPPORTED_MEDIA_TYPE


    is_valid, error_message = validate_relay_notif(request.data)

    if not is_valid:
        if error_message.startswith("Parsing error") or error_message == "Invalid Content-Type":
            return error_message, HTTPStatus.UNSUPPORTED_MEDIA_TYPE
        return error_message, HTTPStatus.BAD_REQUEST

    try: 
        data_string = request.data.decode('utf-8')
        if req_content_type == MIME_APPLICATION_JSON:
            message = json.loads(data_string)
        elif req_content_type == MIME_APPLICATION_XML:
            message = xmltodict.parse(data_string, process_namespaces=False)
            message = strip_namespace(message)
        elif req_content_type == MIME_APPLICATION_CBOR:
            parsed_cbor = bytes.fromhex(data_string.decode('utf-8'))
            message = cbor2.loads(parsed_cbor)

    #  Produce message to Kafka 
        producer.produce(
            KAFKA_TOPIC_NAME,
            key=None,
            value=json.dumps(message),
            callback=delivery_report
        )
        producer.flush()
        app.logger.info(f"Message sent to Kafka topic '{KAFKA_TOPIC_NAME}': {message}")
    except Exception as e:
        app.logger.error(f"Error sending message to Kafka: {e}")
        return "Internal Server Error", HTTPStatus.INTERNAL_SERVER_ERROR
    
    POST_BODY_SIZE.set(len(request.data))
    return '', HTTPStatus.NO_CONTENT

# Metrics for Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status_code', 'content_type'])
REQUEST_LATENCY_CAPABILITIES = Gauge('http_request_latency_seconds_capabilities', 'Latency of HTTP GET /capabilities')
REQUEST_LATENCY_NOTIFICATION_JSON = Gauge('http_request_latency_seconds_notification_json', 'Latency of HTTP POST /relay-notification (JSON)')
REQUEST_LATENCY_NOTIFICATION_XML = Gauge('http_request_latency_seconds_notification_xml', 'Latency of HTTP POST /relay-notification (XML)')
POST_BODY_SIZE = Gauge('post_request_body_size_bytes', 'Size of POST request body in bytes')

@app.before_request
def start_timer():
    """Start the timer before processing the request."""
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    """Record metrics after processing the request."""
    content_type = request.headers.get('Content-Type', 'unknown')
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status_code=response.status_code,
        content_type=content_type
    ).inc()
    latency = time.time() - request.start_time
    if request.path == '/capabilities' and request.method == 'GET':
        REQUEST_LATENCY_CAPABILITIES.set(latency)
    elif request.path == '/relay-notification' and request.method == 'POST':
        if content_type == MIME_APPLICATION_JSON:
            REQUEST_LATENCY_NOTIFICATION_JSON.set(latency)
        elif content_type == MIME_APPLICATION_XML:
            REQUEST_LATENCY_NOTIFICATION_XML.set(latency)

    return response

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

if __name__ == '__main__':
    app.run()