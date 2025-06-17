---

# Publisher

---

## Usage

### Running via Docker Compose (Recommended)

When using the full project setup, the publisher launches automatically as part of your Docker Compose stack.

1.  Ensure you're in the **root directory** of your project.
2.  Start the entire Docker Compose stack:
    ```bash
    docker-compose up --build -d
    ```
    (You can specifically target the publisher service with `docker-compose up --build -d publisher_app`, but typically you'll want the whole stack running).

The `publisher_app` service is configured in `docker-compose.yml` to automatically connect to your collector service (`flask_collector` or `fastapi_collector`) within the Docker network.

### Running Manually (for development/testing)

You can also run the `publisher.py` script directly on your host system for development or specific testing scenarios.

1.  **Install dependencies**:
    First, ensure you've set up a Python virtual environment (as outlined in the main `INSTALLATION.md`). Then, install the required packages:
    ```bash
    cd python/publisher/
    pip install -r requirements.txt
    ```

2.  **Execute the script**:
    The script requires the IP address (or hostname) of your collector and supports several configuration options:

    ```bash
    python3 publisher.py <COLLECTOR_IP_OR_HOSTNAME> --port <PORT> [OPTIONS]
    ```

    **Arguments:**
    * `<COLLECTOR_IP_OR_HOSTNAME>`: The IP address (IPv4 or IPv6) or hostname of the collector (e.g., `localhost` if running locally, or `flask_collector` if connecting to a Dockerized collector from another container in the same network).

    **Options:**
    * `-t, --time <seconds>`: Sets a fixed time interval (in seconds) between sending notifications (default: 2 seconds).
    * `-r, --random <max_seconds>`: Sends notifications at random intervals, where the interval is a random number between 0 and `max_seconds`. This option is mutually exclusive with `--time`.
    * `-p, --port <port_number>`: Specifies the port number of the collector (default: 443 if not specified).
    * `-v, --verbose`: Enables verbose output, providing more detailed information during execution.
    * `--num-retries <count>`: Defines the number of times the publisher will retry sending a notification if a failure occurs (default: 3).

    **Examples:**
    ```bash
    # Send notifications every 5 seconds to a collector running on localhost:8080 with verbose output
    python3 publisher.py localhost --port 8080 --time 5 -v
    ```
    ```bash
    python3 publisher.py flask_collector --port 8080 --time 2
    ```