# Installation Guide

This document provides instructions to install the necessary dependencies and run the https-notif draft implementation.

## Prerequisites

Ensure you have **Python 3.7+** and **Docker** installed on your system.

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/your-repository-url.git
cd your-repository-directory
```

### 2. Install Python Dependencies

Use `pip` to install the required Python packages. Ensure you're using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r python/requirements.txt
```

### 3. Set Up Kafka and InfluxDB

- **Run InfluxDB using Docker**:
  Use Docker Compose to set up InfluxDB:

  ```bash
  docker-compose up -d
  ```

- **Access InfluxDB**:
  Go to `localhost:8086` in your browser and sign up for an account.

- **Update .env File**:
  After signing up, copy the operator API token, Org, and Bucket and add them to your `.env` file.

- **Run Kafka Consumer**:
  Start the Kafka consumer to listen for relay notifications:

  ```bash
  python3 python/flask_impl/kafka_consumer.py
  ```

### 4. Run Flask or FastAPI Application

#### Flask:

To run the Flask application, use the following commands for development or production:

- **Development**:

  ```bash
  flask run --host=127.0.0.1 --port=8080 --cert=../../certs/server.crt --key=../../certs/server.key
  ```

- **Production**:

  ```bash
  gunicorn -w 5 --certfile ../../certs/server.crt --keyfile ../../certs/server.key -b 127.0.0.1:4433 app:app
  ```

#### FastAPI:

To run the FastAPI application with SSL:

```bash
uvicorn main:app --host 127.0.0.1 --port 8080 --ssl-keyfile ../../certs/server.key --ssl-certfile ../../certs/server.crt
```
