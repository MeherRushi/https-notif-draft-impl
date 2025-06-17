# Installation Guide

This document provides instructions to install the necessary dependencies and run the HTTPS notification draft implementation.

## Prerequisites

Ensure you have **Python 3.7+** (for running local utility scripts) and **Docker Compose** installed on your system. 
Docker Compose is typically bundled with Docker Desktop on Windows/macOS, or can be installed separately on Linux.

---

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/MeherRushi/https-notif-draft-impl.git
cd https-notif-draft-impl
```

---

### 2. Prepare Environment Variables and Certificates

#### a. Configure Environment Variables


1.  **Copy the sample environment file**:

    ```bash
    cd python/flask_impl/
    cp .env.sample .env
    ```

2.  **Edit the `.env` file**:
    **Open the newly created `.env` file** in a text editor. Populate it with specific values.

    * **Example `.env` content:**
        ```
        INFLUXDB_TOKEN="your_influxdb_admin_token"
        INFLUXDB_ORG="your_influxdb_organization"
        INFLUXDB_BUCKET="your_influxdb_bucket"
        ```
    * **Important**: These values should match what you've configured for the `influxdb` service's `DOCKER_INFLUXDB_INIT_*` environment variables in your `docker-compose.yml`.

#### b. Setup SSL Certificates

The Collector (Flask/FastAPI) applications utilize SSL certificates for secure communication. Ensure your `certs` directory, located at the root of your project, contains `server.crt` and `server.key`.

If you're setting up for local testing and don't have existing certificates, you can generate self-signed ones using OpenSSL:

```bash
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -nodes -keyout certs/server.key -out certs/server.crt -days 365 -subj "/CN=localhost"
```
**Note:** For production deployments, always use certificates issued by a trusted Certificate Authority.

---

### 3. Set Up Python Virtual Environment and Dependencies (for local scripts)

While the main applications are containerized, any local utility scripts (like `read_db.py`) or local development of the applications will require Python and their dependencies to be installed on your host machine. It's highly recommended to use a virtual environment to manage these dependencies.

1.  **Create a virtual environment**:
    Navigate to your project's root directory and run:
    ```bash
    python3 -m venv venv
    ```
2.  **Activate the virtual environment**:
    ```bash
    source venv/bin/activate
    ```
3.  **Install Python dependencies**:
    Install the dependencies required for your local scripts. For instance, to install dependencies for `read_db.py`:
    ```bash
    pip install -r python/flask_impl/requirements.txt
    ```
    If you plan to run publisher or collector locally, install their dependencies too.

---

### 4. Set Up and Run All Services with Docker Compose

This single command will orchestrate your entire environment. It will build all necessary Docker images, create the network, and start all services, including Zookeeper, Kafka, InfluxDB, Prometheus, Grafana, your Flask/FastAPI Collector, and your Publisher.

Navigate to the root directory of your cloned repository (where `docker-compose.yml` is located) and run:

```bash
docker-compose up --build -d
```

* `--build`: Ensures that any changes to your application's `Dockerfile`s are incorporated. This is crucial if you've modified application code or dependencies.
    * The Flask Collector's image will be built using `python/flask_impl/Dockerfile`.
    * The Kafka Consumer's image will be built using `python/flask_impl/kafka_consumer.Dockerfile`.
    * The Publisher's image will be built using `python/publisher/Dockerfile`.
* `-d`: Runs the containers in detached mode (in the background).

---

### 5. Initial InfluxDB Setup

After the services are up, you might need to perform a one-time setup for InfluxDB, depending on how you've configured its initial credentials in `docker-compose.yml`.

1.  **Access InfluxDB UI**: Open your web browser and go to `https://localhost:8086`.
2.  **Initial Setup**: Follow the on-screen prompts to set up your initial user, organization, and bucket if they weren't fully configured via environment variables.
3.  **Retrieve Token**: After setup, navigate to "Data" -> "API Tokens" and copy your **Operator Token** or create a new "All Access API Token".
4.  **Verify `docker-compose.yml` and `.env`**:
    * Ensure the `INFLUXDB_TOKEN`, `INFLUXDB_ORG`, and `INFLUXDB_BUCKET` environment variables in your `docker-compose.yml` match the values you configured/retrieved from InfluxDB.
    * Similarly, ensure your local `.env` file (for `read_db.py`) has these correct values.

---

### 6. Verify Running Services and Data Flow

You can check the status of your services and view their logs to confirm everything is running as expected.

* **Check Service Status**:
    ```bash
    docker-compose ps
    ```
    All services should show `Up` or `healthy`.
    `kafka_topic_creator` will show as `Exited`

* **View Logs (e.g., Publisher to Collector flow)**:
    ```bash
    docker-compose logs -f publisher_app
    docker-compose logs -f flask_collector
    docker-compose logs -f kafka_consumer_app
    ```
    You should observe `publisher_app` successfully sending data, `flask_collector` receiving and processing it, and `kafka_consumer_app` consuming from Kafka and writing to InfluxDB.


* **Read data inserted in InfluxDB**:
    **InfluxDB UI**: `https://localhost:8086`

    or run `python/flask_impl/read_db.py` 

    ---

    ### 7. Setting Up Grafana Dashboard with Prometheus Data Source

    Once Grafana is running, you can configure it to visualize metrics collected by Prometheus:

    1. **Access Grafana**:  
      Open your browser and go to [http://localhost:3000](http://localhost:3000).  
      Login with the default credentials (`admin` / `admin`).

    2. **Add Prometheus as a Data Source**:
      - In the left sidebar, click the gear icon (⚙️) for **Configuration**.
      - Select **Data Sources** and click **Add data source**.
      - Choose **Prometheus**.
      - Set the **URL** to `http://prometheus:9090` (if using Docker Compose, this internal name works; otherwise, use `http://localhost:9090`).
      - Click **Save & Test** to verify the connection.

    3. **Create a Dashboard**:
      - Click the plus icon (+) in the sidebar and select **Dashboard**.
      - Click **Add new panel**.
      - In the query editor, select **Prometheus** as the data source and enter your desired Prometheus query (e.g., `up`, `http_requests_total`, etc.).
      - Configure visualization options as needed.
      - Click **Apply** to save the panel.

    4. **Save the Dashboard**:
      - Click the disk icon to save your dashboard for future use.

    You can now monitor your application's metrics in real time using Grafana dashboards powered by Prometheus data.

---


### 8. Stopping and Cleaning Up

To stop all running containers and remove their networks:

```bash
docker-compose down
```

To also remove named volumes (which contain your persistent InfluxDB and Prometheus data), ensuring a completely clean slate:

```bash
docker-compose down -v
```