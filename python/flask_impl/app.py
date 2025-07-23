"""
HTTPS Notification Receiver Flask Application

This application implements an HTTPS notification receiver that supports multiple
encoding formats (JSON, XML, CBOR) and integrates with Kafka for message processing.
It includes Prometheus metrics collection and YANG model validation.
"""

from typing import Dict, List, Tuple, Any, Union, Optional
import json
import re
import time
from http import HTTPStatus

from flask import Flask, request, jsonify, Response
from prometheus_client import Counter, Gauge, generate_latest
import xmltodict
import cbor2
from confluent_kafka import Producer, KafkaError
from yangson import DataModel
from yangson.enumerations import ContentType


# =============================================================================
# CONSTANTS
# =============================================================================

# URN Constants for capabilities
URN_ENCODING_JSON = "urn:ietf:capability:https-notif-receiver:encoding:json"
URN_ENCODING_XML = "urn:ietf:capability:https-notif-receiver:encoding:xml"
URN_ENCODING_CBOR = "urn:ietf:capability:https-notif-receiver:encoding:cbor"

# JSON Structure Keys
JSON_RECEIVER_CAPABILITIES = "receiver-capabilities"
JSON_RECEIVER_CAPABILITY = "receiver-capability"

# HTTP Headers
UHTTPS_CONTENT_TYPE = 'Content-Type'
UHTTPS_ACCEPT = 'Accept'

# MIME Types
MIME_APPLICATION_XML = "application/xml"
MIME_APPLICATION_JSON = "application/json"
MIME_APPLICATION_CBOR = "application/cbor"

# Kafka Configuration
KAFKA_TOPIC_NAME = 'test-topic'
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'

# YANG Model Configuration
YANG_DIR_PATH = "../../yang_modules/"
YANG_LIBRARY_PATH = "../../yang_modules/yang-library.json"

# Collector Capabilities Configuration
COLLECTOR_CAPABILITIES = {
    'json_capable': True,
    'xml_capable': True,
    'cbor_capable': True,
}

# Reply Support Configuration
REPLY_SUPPORT = {
    'json': True,
    'xml': True,
    'cbor': True,
}


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

app = Flask(__name__)

# Initialize Kafka Producer
producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

# Initialize YANG Data Model
try:
    data_model = DataModel.from_file(YANG_LIBRARY_PATH, [YANG_DIR_PATH])
except Exception as e:
    app.logger.error(f"Failed to initialize YANG data model: {e}")
    data_model = None

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests', 
    ['method', 'endpoint', 'status_code', 'content_type']
)
REQUEST_LATENCY_CAPABILITIES = Gauge(
    'http_request_latency_seconds_capabilities', 
    'Latency of HTTP GET /capabilities'
)
REQUEST_LATENCY_NOTIFICATION_JSON = Gauge(
    'http_request_latency_seconds_notification_json', 
    'Latency of HTTP POST /relay-notification (JSON)'
)
REQUEST_LATENCY_NOTIFICATION_XML = Gauge(
    'http_request_latency_seconds_notification_xml', 
    'Latency of HTTP POST /relay-notification (XML)'
)
POST_BODY_SIZE = Gauge(
    'post_request_body_size_bytes', 
    'Size of POST request body in bytes'
)


# =============================================================================
# KAFKA UTILITIES
# =============================================================================

def delivery_report(err: Optional[KafkaError], msg) -> None:
    """
    Kafka message delivery callback function.
    
    Args:
        err: Kafka error if delivery failed, None if successful
        msg: Message object containing delivery information
    """
    if err:
        app.logger.error(f"Message delivery failed: {err}")
    else:
        app.logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# =============================================================================
# DATA PROCESSING UTILITIES
# =============================================================================

def strip_namespace(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Recursively removes namespaces from XML keys in nested data structures.
    
    Args:
        data: The data structure to process (dict, list, or primitive)
        
    Returns:
        The data structure with namespaces stripped from keys
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            # Extract key after the last colon (namespace separator)
            stripped_key = key.split(':')[-1] if ':' in key else key
            new_data[stripped_key] = strip_namespace(value)
        return new_data
    elif isinstance(data, list):
        return [strip_namespace(item) for item in data]
    else:
        return data


def process_xml_interface_data(json_data: Dict[str, Any]) -> None:
    """
    Process and convert XML interface data types to appropriate Python types.
    
    Args:
        json_data: The parsed JSON data from XML conversion
    """
    try:
        interfaces = json_data['ietf-https-notif:notification']['interface_data']['interface']
        
        # Ensure interfaces is always a list
        if isinstance(interfaces, dict):
            interfaces = [interfaces]
        
        # Process each interface
        for interface in interfaces:
            # Convert 'enabled' string to boolean
            if 'enabled' in interface:
                interface['enabled'] = interface['enabled'] != 'false'
            
            # Convert 'if-index' to integer
            if 'if-index' in interface and isinstance(interface['if-index'], str):
                interface['if-index'] = int(interface['if-index'])
            
            # Convert statistics values to integers
            if 'statistics' in interface:
                stats_keys = ['in-discards', 'in-errors', 'in-unknown-protos', 
                             'out-discards', 'out-errors']
                for key in stats_keys:
                    if (key in interface['statistics'] and 
                        isinstance(interface['statistics'][key], str)):
                        interface['statistics'][key] = int(interface['statistics'][key])
        
        # Update the original data structure
        json_data['ietf-https-notif:notification']['interface_data']['interface'] = interfaces
        
    except KeyError as e:
        app.logger.warning(f"Expected key not found in interface data: {e}")
    except (ValueError, TypeError) as e:
        app.logger.error(f"Type conversion error in interface data: {e}")


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_relay_notif(data_string: bytes) -> Tuple[bool, Optional[str]]:
    """
    Validate the relay notification data against the YANG model.
    
    Args:
        data_string: Raw request data as bytes
        
    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not data_model:
        return False, "YANG data model not initialized"
    
    req_content_type = request.headers.get(UHTTPS_CONTENT_TYPE)
    
    try:
        # Parse data based on content type
        if req_content_type == MIME_APPLICATION_JSON:
            json_data = json.loads(data_string.decode('utf-8'))
            
        elif req_content_type == MIME_APPLICATION_XML:
            json_data = xmltodict.parse(data_string.decode('utf-8'), process_namespaces=False)
            process_xml_interface_data(json_data)
            
        elif req_content_type == MIME_APPLICATION_CBOR:
            json_data = cbor2.loads(data_string)
            
        else:
            return False, "Invalid Content-Type"

    except (json.JSONDecodeError, UnicodeDecodeError, cbor2.CBORDecodeError) as e:
        app.logger.error(f"Parsing error for {req_content_type}: {e}")
        return False, "Parsing error: invalid data format"
    except Exception as e:
        app.logger.error(f"Unexpected parsing error: {e}")
        return False, "Parsing error: unexpected format issue"

    # Validate against YANG model
    try:
        instance = data_model.from_raw(json_data)
        instance.validate(ctype=ContentType.all)
        return True, None
    except Exception as e:
        app.logger.error(f"YANG validation error: {e}")
        return False, "Validation error: data does not conform to the YANG module"


# =============================================================================
# CAPABILITY BUILDING FUNCTIONS
# =============================================================================

def build_capabilities_data() -> List[str]:
    """
    Build the list of supported capabilities based on configuration.
    
    Returns:
        List of capability URN strings
    """
    capabilities = []
    
    if COLLECTOR_CAPABILITIES['json_capable']:
        capabilities.append(URN_ENCODING_JSON)
    if COLLECTOR_CAPABILITIES['xml_capable']:
        capabilities.append(URN_ENCODING_XML)
    if COLLECTOR_CAPABILITIES['cbor_capable']:
        capabilities.append(URN_ENCODING_CBOR)
    
    return capabilities


def build_xml_response(capabilities_data: List[str]) -> str:
    """
    Build XML response for capabilities.
    
    Args:
        capabilities_data: List of capability URN strings
        
    Returns:
        XML string representation of capabilities
    """
    xml_content = '<receiver-capabilities>\n'
    for capability in capabilities_data:
        xml_content += f'    <receiver-capability>{capability}</receiver-capability>\n'
    xml_content += '</receiver-capabilities>'
    return xml_content


def build_json_response(capabilities_data: List[str]) -> str:
    """
    Build JSON response for capabilities.
    
    Args:
        capabilities_data: List of capability URN strings
        
    Returns:
        JSON string representation of capabilities
    """
    return json.dumps({
        JSON_RECEIVER_CAPABILITIES: {
            JSON_RECEIVER_CAPABILITY: capabilities_data
        }
    }, indent=2)


def build_cbor_response(capabilities_data: List[str]) -> str:
    """
    Build CBOR response for capabilities.
    
    Args:
        capabilities_data: List of capability URN strings
        
    Returns:
        CBOR hex string representation of capabilities
    """
    data = cbor2.dumps({
        JSON_RECEIVER_CAPABILITIES: {
            JSON_RECEIVER_CAPABILITY: capabilities_data
        }
    }).hex()
    return data


# =============================================================================
# CONTENT NEGOTIATION FUNCTIONS
# =============================================================================

def get_q_value(accept_header: str, media_type: str) -> float:
    """
    Extract the quality (q) value for a specific media type from Accept header.
    
    Args:
        accept_header: The Accept header value
        media_type: The media type to search for
        
    Returns:
        The q-value (0.0 to 1.0), defaults to 1.0 if not specified
    """
    pattern = re.compile(rf"{re.escape(media_type)}(;q=([0-9.]+))?")
    match = pattern.search(accept_header)
    if match:
        q_value = match.group(2)
        return float(q_value) if q_value else 1.0
    return 0.0


def get_default_response(capabilities_data: List[str]) -> Tuple[str, HTTPStatus, Dict[str, str]]:
    """
    Get the default response based on reply support configuration.
    
    Args:
        capabilities_data: List of capability URN strings
        
    Returns:
        Tuple of (response_body, status_code, headers)
    """
    if REPLY_SUPPORT['xml']:
        return (build_xml_response(capabilities_data), 
                HTTPStatus.OK, 
                {'Content-Type': MIME_APPLICATION_XML})
    elif REPLY_SUPPORT['json']:
        return (build_json_response(capabilities_data), 
                HTTPStatus.OK, 
                {'Content-Type': MIME_APPLICATION_JSON})
    elif REPLY_SUPPORT['cbor']:
        return (build_cbor_response(capabilities_data), 
                HTTPStatus.OK, 
                {'Content-Type': MIME_APPLICATION_CBOR})
    
    return (jsonify({"error": "No valid capabilities found"}), 
            HTTPStatus.INTERNAL_SERVER_ERROR, {})


def respond_with_content_type(accept_header: str, 
                            capabilities_data: List[str]) -> Tuple[str, HTTPStatus, Dict[str, str]]:
    """
    Respond based on Accept header and content capabilities, considering q-values.
    
    Args:
        accept_header: The Accept header from the request
        capabilities_data: List of capability URN strings
        
    Returns:
        Tuple of (response_body, status_code, headers)
    """
    q_xml = get_q_value(accept_header, MIME_APPLICATION_XML)
    q_json = get_q_value(accept_header, MIME_APPLICATION_JSON)
    q_cbor = get_q_value(accept_header, MIME_APPLICATION_CBOR)

    # Validate q-values are in valid range
    if not all(0 <= q <= 1 for q in [q_xml, q_json, q_cbor]):
        return (jsonify({"error": "Invalid q value"}), HTTPStatus.BAD_REQUEST, {})

    # If all q-values are 0, return default response
    if q_json == 0 and q_xml == 0 and q_cbor == 0:
        return get_default_response(capabilities_data)
    
    # Find the highest q-value and corresponding supported format
    q_max = max(q_xml, q_json, q_cbor)
    
    if q_max == q_xml and REPLY_SUPPORT['xml']:
        return (build_xml_response(capabilities_data), 
                HTTPStatus.OK, 
                {'Content-Type': MIME_APPLICATION_XML})
    elif q_max == q_json and REPLY_SUPPORT['json']:
        return (build_json_response(capabilities_data), 
                HTTPStatus.OK, 
                {'Content-Type': MIME_APPLICATION_JSON})
    elif q_max == q_cbor and REPLY_SUPPORT['cbor']:
        return (build_cbor_response(capabilities_data), 
                HTTPStatus.OK, 
                {'Content-Type': MIME_APPLICATION_CBOR})

    return (jsonify({"error": "Not acceptable"}), HTTPStatus.NOT_ACCEPTABLE, {})


# =============================================================================
# MESSAGE PROCESSING FUNCTIONS
# =============================================================================

def process_and_send_to_kafka(data_string: bytes, content_type: str) -> Tuple[bool, str]:
    """
    Process the notification data and send it to Kafka.
    
    Args:
        data_string: Raw request data
        content_type: Content type of the request
        
    Returns:
        Tuple of (success: bool, error_message: str)
    """
    try:
        # Parse the message based on content type
        if content_type == MIME_APPLICATION_JSON:
            message = json.loads(data_string.decode('utf-8'))
        elif content_type == MIME_APPLICATION_XML:
            message = xmltodict.parse(data_string.decode('utf-8'), process_namespaces=False)
            message = strip_namespace(message)
        elif content_type == MIME_APPLICATION_CBOR:
            message = cbor2.loads(data_string)
        else:
            return False, f"Unsupported content type: {content_type}"

        # Send message to Kafka
        producer.produce(
            KAFKA_TOPIC_NAME,
            key=None,
            value=json.dumps(message),
            callback=delivery_report
        )
        producer.flush()
        
        app.logger.info(f"Message sent to Kafka topic '{KAFKA_TOPIC_NAME}'")
        return True, ""
        
    except Exception as e:
        error_msg = f"Error processing/sending message to Kafka: {e}"
        app.logger.error(error_msg)
        return False, error_msg


# =============================================================================
# FLASK ROUTES
# =============================================================================

@app.route('/capabilities', methods=['GET'])
def get_capabilities() -> Union[Tuple[str, HTTPStatus, Dict[str, str]], Tuple[str, HTTPStatus]]:
    """
    Handle GET requests to /capabilities endpoint.
    
    Returns capabilities based on Accept header preferences or default format.
    """
    capabilities_data = build_capabilities_data()
    accept_header = request.headers.get(UHTTPS_ACCEPT)
    
    app.logger.info(f"Capabilities request with Accept header: {accept_header}")
    
    if accept_header:
        return respond_with_content_type(accept_header, capabilities_data)
    
    return get_default_response(capabilities_data)


@app.route('/relay-notification', methods=['POST'])
def post_notification() -> Tuple[str, HTTPStatus]:
    """
    Handle POST requests to /relay-notification endpoint.
    
    Validates the notification data and forwards it to Kafka if valid.
    """
    req_content_type = request.headers.get(UHTTPS_CONTENT_TYPE)

    # Validate Content-Type header
    if req_content_type is None:
        return "Content-type is None -> Empty Body Notification", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    if req_content_type not in [MIME_APPLICATION_JSON, MIME_APPLICATION_XML, MIME_APPLICATION_CBOR]:
        return "Unsupported Media Type", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # Check if the content type is supported by collector capabilities
    if ((req_content_type == MIME_APPLICATION_JSON and not COLLECTOR_CAPABILITIES['json_capable']) or
        (req_content_type == MIME_APPLICATION_XML and not COLLECTOR_CAPABILITIES['xml_capable']) or
        (req_content_type == MIME_APPLICATION_CBOR and not COLLECTOR_CAPABILITIES['cbor_capable'])):
        return f"{req_content_type} encoding not supported", HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    # Validate the notification data
    is_valid, error_message = validate_relay_notif(request.data)
    if not is_valid:
        if error_message and (error_message.startswith("Parsing error") or 
                             error_message == "Invalid Content-Type"):
            return error_message, HTTPStatus.UNSUPPORTED_MEDIA_TYPE
        return error_message or "Validation failed", HTTPStatus.BAD_REQUEST

    # Process and send to Kafka
    success, error_msg = process_and_send_to_kafka(request.data, req_content_type)
    if not success:
        return "Internal Server Error", HTTPStatus.INTERNAL_SERVER_ERROR
    
    # Record metrics
    POST_BODY_SIZE.set(len(request.data))
    
    return '', HTTPStatus.NO_CONTENT


@app.route('/metrics', methods=['GET'])
def metrics() -> Response:
    """
    Prometheus metrics endpoint.
    
    Returns:
        Prometheus metrics in text format
    """
    return Response(generate_latest(), mimetype="text/plain")


# =============================================================================
# FLASK MIDDLEWARE
# =============================================================================

@app.before_request
def start_timer() -> None:
    """Start the timer before processing each request for latency metrics."""
    request.start_time = time.time()


@app.after_request
def record_metrics(response: Response) -> Response:
    """
    Record Prometheus metrics after processing each request.
    
    Args:
        response: Flask response object
        
    Returns:
        The unmodified response object
    """
    content_type = request.headers.get('Content-Type', 'unknown')
    
    # Record request count metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status_code=response.status_code,
        content_type=content_type
    ).inc()
    
    # Record latency metrics
    if hasattr(request, 'start_time'):
        latency = time.time() - request.start_time
        
        if request.path == '/capabilities' and request.method == 'GET':
            REQUEST_LATENCY_CAPABILITIES.set(latency)
        elif request.path == '/relay-notification' and request.method == 'POST':
            if content_type == MIME_APPLICATION_JSON:
                REQUEST_LATENCY_NOTIFICATION_JSON.set(latency)
            elif content_type == MIME_APPLICATION_XML:
                REQUEST_LATENCY_NOTIFICATION_XML.set(latency)

    return response


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    app.run()