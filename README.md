# Network Gateway

It started as a lightweight, educational HTTP server, and it turned into a whole gate to subnets.
It was created to practice networking concepts like TCP connection handling, HTTP parsing, and basic traffic filtering without relying on external web frameworks.
It now also decides *where a request should go*: the **GateWay** maps a destination IP to a station in a simulated network and finds the cheapest route to it.

## Key Features
* **Raw TCP Sockets:** Handles client-server connections directly at the transport layer.
* **Custom HTTP Parsing:** Extracts HTTP methods, paths, and headers from incoming byte streams.
* **Layered Filtering:** Applies basic IP subnet blocking (CIDR) and regex-based request inspection.
* **Destination Mapping:** Finds which network a destination IP belongs to using longest-prefix matching.
* **Shortest-Path Routing:** Models a network as a weighted graph and routes with Dijkstra's algorithm. The hops are simulated.
* **Dockerized:** Packaged in a container for a clean, isolated execution environment.

## How a request travels
 
```text
Client request
      |
      v
+----------------------+
| 1. Blacklist         |-- blocked    --> 403
| 2. Parse             |-- malformed  --> 400
| 3. WAF               |-- suspicious --> 403
| 4. Destination IP    |-- invalid    --> 400
| 5. Subnet lookup     |-- unmapped   --> 404
| 6. Dijkstra, GateWay |-- no route   --> 502
+----------------------+
      |
      v
200 OK + the route
```
 
The checks run top to bottom, and the first one that fails answers the client.
 
## The simulated network
 
```text
              +----- 4 -------+
              |               |
GateWay --2-- A --1-- B --1-- C
   |                  |
   +------ 5 ---------+
 
A = 10.0.0.0/8     B = 192.168.1.0/24     C = 10.1.0.0/16
```

The routing is a simulation: the gateway computes the whole route at once and logs each hop, while a real router decides only the next hop.

## Configuration
 
`blacklist.txt` lists blocked client IPs or networks, `topology.txt` holds links as `STATION_A STATION_B COST`, and `subnets.txt` maps `CIDR STATION` (the most specific network wins). 

## Technologies Used

* Python with Standard Library: `socket`, `argparse`, `re`,`heapq`, `urllib.parse`.
* Docker

## Run

### Run locally
 
```bash
python main.py                  # port 8085, use -b FILE for another blacklist
python test.py                  # in a second terminal, checks the ACL, routing, server and WAF
curl -i -H "User-Agent: Test" -H "X-Destination-IP: 10.1.2.3" http://127.0.0.1:8085/
```
  
### Run via Docker

**Build the image:**

```bash
docker build -t network-gateway .
```

**Run the server:**

```bash
docker run --rm -p 127.0.0.1:8085:8085 network-gateway
```

The server listens on port `8085`. Publishing on `127.0.0.1` keeps it reachable only from your machine.

---

> **Note:** It is a demo project applying hands-on networking concepts. It is not intended as a production-grade HTTP server or WAF.
