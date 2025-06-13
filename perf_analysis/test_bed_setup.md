
## Setup Guide: Network Namespace Simulation

This guide sets up two isolated network namespaces connected through a virtual bridge to simulate network communication between a client and a web server.

Below is an image describing the setup : <br>
![setup](/perf_analysis/setup.png)

---

### Step 1: Create Network Namespaces

Create two network namespaces to isolate the network stack for different processes:

```bash
sudo ip netns add publisher_ns
sudo ip netns add collector_ns
```

- `publisher_ns` will act as the client.
- `collector_ns` will run the web server.

Namespaces function like lightweight virtual machines for networking.

---

### Step 2: Create a Linux Bridge (`br0`)

A Linux bridge acts as a virtual Ethernet switch, enabling communication between the namespaces.

```bash
sudo ip link add br0 type bridge
```

- Creates a Layer 2 bridge named `br0`.

---

### Step 3: Assign an IP Address to the Bridge

Assigning an IP address to the bridge allows the host machine to communicate with the namespaces.

```bash
sudo ip addr add 192.168.1.254/24 dev br0
sudo ip link set br0 up
```

---

### Step 4: Create Virtual Ethernet Pairs

Create two `veth` (virtual Ethernet) pairs to connect the namespaces to the bridge:

```bash
sudo ip link add veth0 type veth peer name veth1
sudo ip link add veth2 type veth peer name veth3
```

- `veth0` ↔ `veth1`: connects `publisher_ns` to the bridge.
- `veth2` ↔ `veth3`: connects `collector_ns` to the bridge.

Each veth pair acts like a virtual cable between two interfaces.

---

### Step 5: Move Interfaces to Namespaces

Move one end of each veth pair into its respective namespace:

```bash
sudo ip link set veth0 netns publisher_ns
sudo ip link set veth2 netns collector_ns
```

- `veth0` goes into `publisher_ns`.
- `veth2` goes into `collector_ns`.

---

### Step 6: Attach Interfaces to the Bridge

Attach the host-side interfaces (`veth1`, `veth3`) to the bridge:

```bash
sudo ip link set veth1 master br0
sudo ip link set veth3 master br0
sudo ip link set veth1 up
sudo ip link set veth3 up
```

---

### Step 7: Assign IP Addresses in Namespaces

Assign IP addresses to the veth interfaces inside the namespaces:

```bash
sudo ip netns exec publisher_ns ip addr add 192.168.1.1/24 dev veth0
sudo ip netns exec collector_ns ip addr add 192.168.1.2/24 dev veth2
```

- `publisher_ns`: 192.168.1.1
- `collector_ns`: 192.168.1.2

---

### Step 8: Bring Up Interfaces

Activate the veth and loopback interfaces inside each namespace:

```bash
sudo ip netns exec publisher_ns ip link set veth0 up
sudo ip netns exec collector_ns ip link set veth2 up

sudo ip netns exec publisher_ns ip link set lo up
sudo ip netns exec collector_ns ip link set lo up
```

---

### Step 9: Test Connectivity

Verify that the namespaces can reach each other:

```bash
sudo ip netns exec publisher_ns ping -c 3 192.168.1.2
```

If successful, communication between namespaces is working via the bridge.

---

### Step 10: Run a Web Server in `collector_ns`

Start a test HTTP server:

```bash
sudo ip netns exec collector_ns python3 -m http.server 8080 --bind 192.168.1.2
```

Test from `publisher_ns`:

```bash
sudo ip netns exec publisher_ns curl http://192.168.1.2:8080
```

To run the Flask server instead:

```bash
sudo ip netns exec collector_ns flask run --host=192.168.1.2 --port=8080 --cert=../../certs/server.crt --key=../../certs/server.key
```

Make sure you are in the correct directory before running this command.

---

### Step 11: Allow Host to Access the Web Server

Add a route on the host to reach the namespace network:

```bash
sudo ip route add 192.168.1.0/24 dev br0
```

Now the host can reach services inside `collector_ns`:

```bash
curl http://192.168.1.2:8080
```

The host should now receive a response from the web server running in the namespace.