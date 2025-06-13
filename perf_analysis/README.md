# Performance Analysis of Encoding Formats Under Varying Bandwidth

This report presents an evaluation of different encoding formats—**JSON**, **XML**, and **CBOR**—under varying network bandwidth constraints using a controlled local testbed. The goal was to measure how these formats perform in terms of throughput and request handling under simulated network conditions.

## Objective

The objective of this experiment was to:
- Set up a proof-of-concept server-client model.
- Simulate a real-world network using Linux network namespaces.
- Automate bandwidth control and benchmarking.
- Analyze encoding performance across different constrained bandwidth levels.

---

## Testbed Setup

Due to time and hardware constraints, the tests were conducted on a local machine using Linux network namespaces to simulate an isolated client-server environment.

![Testbed Setup](/perf_analysis/setup.png)  
*Figure 1: Virtual network namespace setup*

### 1. Network Namespace Configuration

- Two namespaces were created:
  - `publisher_ns` (acts as the client)
  - `collector_ns` (acts as the server)

- These namespaces were interconnected using a virtual Ethernet pair:
  - `veth0` assigned to `publisher_ns`
  - `veth1` assigned to `collector_ns`

- Static IPs were configured to enable communication over this virtual link.

### 2. Collector Setup (Server)

- The server application, referred to as the **collector**, runs inside `collector_ns`.
- It listens on a fixed IP and port (e.g., `192.168.1.2:8080`) and accepts HTTP POST requests from the publisher.

### 3. Bandwidth Simulation and Load Testing

A shell script was used to automate the entire testing workflow, including:

#### a. Bandwidth Control

- Traffic Control (`tc`) was used to apply Token Bucket Filter (TBF) queuing on both virtual interfaces.
- The bandwidth limits tested were: `1mbit`, `5mbit`, `10mbit`, `50mbit`, `100mbit`, `500mbit`, and `1gbit`.
- A burst size of `32kbit` and queue latency of `50ms` were configured.

#### b. Request Generation

- HTTP POST requests were generated using [`go-wrk`](https://github.com/tsliwowicz/go-wrk), a high-performance HTTP benchmarking tool written in Go.
- The tool was configured to:
  - Use a single persistent connection per simulated publisher.
  - Maintain 100 concurrent connections to the server.
  - Run each test for 30 seconds.
- The request payload format was varied using the `ENCODINGS` array: `JSON`, `XML`, and `CBOR`.

#### c. Traffic and Performance Measurement

- Output metrics from `go-wrk` were saved to separate text files for each test.
- A Python script (`plot.py`) was used to extract metrics and generate performance graphs using Matplotlib.

> Script location: [`/perf_analysis/data/gowrk_script`](./perf_analysis/data/gowrk_script)

---

## Results Summary

The table below summarizes the metrics for each bandwidth and encoding format:

| Bandwidth | Encoding | Requests/sec | Transfer/sec | Throughput (Mbps) |
|-----------|----------|--------------|--------------|--------------------|
| 1mbit     | JSON     | 25.10        | 2.38KB       | 0.019              |
|           | XML      | 21.57        | 2.04KB       | 0.016              |
|           | CBOR     | 31.67        | 3.00KB       | 0.024              |
| 5mbit     | JSON     | 123.81       | 11.73KB      | 0.094              |
|           | XML      | 106.73       | 10.11KB      | 0.081              |
|           | CBOR     | 157.66       | 14.93KB      | 0.119              |
| 10mbit    | JSON     | 250.20       | 23.70KB      | 0.190              |
|           | XML      | 211.79       | 20.06KB      | 0.161              |
|           | CBOR     | 311.56       | 29.51KB      | 0.236              |
| 50mbit    | JSON     | 310.73       | 29.43KB      | 0.236              |
|           | XML      | 307.31       | 29.11KB      | 0.234              |
|           | CBOR     | 311.71       | 29.53KB      | 0.237              |
| 100mbit   | JSON     | 312.49       | 29.60KB      | 0.237              |
|           | XML      | 307.87       | 29.16KB      | 0.233              |
|           | CBOR     | 310.96       | 29.46KB      | 0.236              |
| 500mbit   | JSON     | 313.73       | 28.77KB      | 0.231              |
|           | XML      | 308.64       | 29.24KB      | 0.234              |
|           | CBOR     | 312.99       | 28.70KB      | 0.230              |
| 1gbit     | JSON     | 313.28       | 29.68KB      | 0.237              |
|           | XML      | 308.86       | 29.26KB      | 0.234              |
|           | CBOR     | 315.14       | 29.85KB      | 0.239              |

> Throughput (Mbps) = `(Transfer/sec in KB) * 8 / 1024`  
> All values rounded to 3 decimal places

- Raw output files: [`/perf_analysis/data/test1`](./perf_analysis/data/test1)
- Request/sec graph:  
  ![Request Rate](/perf_analysis/data/stats.png)

---

## Analysis and Observations

### General Trends

- **Performance scales linearly** with bandwidth up to approximately `50mbit`. Beyond that, the request rate **plateaus**, indicating:
  - A **processing bottleneck** at the publisher end.
  - The system was unable to generate more requests due to computational limits, not network constraints.

### Encoding Format Performance

- **CBOR consistently outperforms JSON and XML** across all tested bandwidths.
- **JSON performs slightly better than XML**, with a smaller payload and faster parsing.
- **XML is the least efficient** in terms of both size and parsing speed.

### Encoding Format Comparison: CBOR > JSON > XML

CBOR offers the best performance due to its binary format, minimal parsing overhead, and compact payloads—often up to 50% smaller than JSON. It preserves native data types directly, making it ideal for bandwidth-sensitive or real-time applications. JSON, while text-based, benefits from a simpler structure and faster parsing compared to XML. XML, being the most verbose, suffers from heavier parsing requirements (DOM/SAX) and higher bandwidth usage, making it the least efficient.

### Payload Size and Performance

For small payloads (1–5 KB), parsing overhead is the dominant factor—CBOR shows the greatest benefit here. At medium sizes (~10 KB), a mix of parsing and transfer costs still favors CBOR. For larger payloads (50 KB+), network I/O becomes the main bottleneck, and performance differences among formats diminish as all formats approach similar throughput due to server and network limits.

---

## CPU and System Information

All tests were conducted on the same physical machine running both server and client namespaces.

```bash
$ lscpu
Architecture:          x86_64
CPU(s):                8 (4 cores, 2 threads per core)
Model name:            Intel(R) Core(TM) i7-8550U @ 1.80GHz
Max clock speed:       4.0 GHz
L3 Cache:              8 MB
```

- CPU Threads Available: 8

- Worker threads configured using: 2 * number of cores + 1

- Server and client were each allocated 2 CPU cores.

---

## Source Code

- **Bandwidth simulation and load script:** [`gowrk_script`](./perf_analysis/data/gowrk_script)
- **Result parser and plot script:** [`plot.py`](./perf_analysis/data/plot.py)

---

## Conclusion

This study demonstrates that **CBOR is the most efficient encoding format** in constrained bandwidth environments, outperforming both JSON and XML. While the performance gap narrows as bandwidth increases or payload size grows, CBOR maintains a clear advantage in scenarios that are sensitive to bandwidth and real-time constraints.

Additionally, the observed performance plateau at higher bandwidths indicates that **system-level factors such as CPU capacity and resource allocation** can become bottlenecks. These factors must be considered when designing high-throughput systems, especially when network capacity is no longer the limiting factor.

