import socket
import time
from main import read_entries
from network_acl import build_blacklist, is_blocked
from routing import build_topology, build_subnets, get_route

# Run from the project folder. Part 2 needs the server to be running (python main.py)

# ---------- 1. Direct tests, no server needed ----------
build_blacklist(read_entries("blacklist.txt"))
build_topology(read_entries("topology.txt"))
build_subnets(read_entries("subnets.txt"))

print("\n--- ACL Blacklist Tests ---")
print("[V] Blacklisted IP Blocked" if is_blocked("192.168.1.50") else "[X] Failed: IP should be blocked")
print("[V] Blacklisted Range Blocked" if is_blocked("10.5.5.5") else "[X] Failed: IP should be blocked")
print("[V] Clean IP Allowed" if not is_blocked("8.8.8.8") else "[X] Failed: IP should be allowed")


def check_route(test_name, ip, expected):
    route = get_route(ip)
    if route == expected:
        print(f"[V] {test_name} - Passed")
    else:
        print(f"[X] {test_name} - Failed: got {route}")


print("\n--- Routing Tests ---")
check_route("Most specific network wins (/16 over /8)", "10.1.2.3", ["GateWay", "A", "B", "C"])
check_route("Wider network (/8)", "10.9.9.9", ["GateWay", "A"])
check_route("Cheapest path goes through A", "192.168.1.5", ["GateWay", "A", "B"])
check_route("Unmapped ip gives empty route", "8.8.8.8", [])


# ---------- 2. Tests against the running server ----------
def make_request(path="/", destination="10.1.2.3", user_agent="Test"):
    request = "GET " + path + " HTTP/1.1\r\n"
    if user_agent:
        request += "User-Agent: " + user_agent + "\r\n"
    if destination:
        request += "X-Destination-IP: " + destination + "\r\n"
    return request + "\r\n"


# expected is a text that must appear in the response (a status, or a part of the route)
def check_server(test_name, payload, expected):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 8085))
    s.send(payload.encode('utf-8'))

    response = s.recv(2048).decode('utf-8')
    s.close()

    if expected in response:
        print(f"[V] {test_name} - Passed")
    else:
        print(f"[X] {test_name} - Failed")
    time.sleep(0.1)


print("\n--- Server Tests ---")
try:
    check_server("Valid request, route text", make_request(), "GateWay -> A -> B -> C")
    check_server("Valid request, status", make_request(), "200 OK")
    check_server("Missing destination header", make_request(destination=None), "400 Bad Request")
    check_server("Invalid destination ip", make_request(destination="10.1.2"), "400 Bad Request")
    check_server("Malformed request", "NOT_HTTP_DATA_STREAM\r\n\r\n", "400 Bad Request")
    check_server("Destination not mapped", make_request(destination="8.8.8.8"), "404 Not Found")

    # 502 (station not reachable) needs a station with no links to the gateway, not in the sample files

    print("\n--- WAF Tests ---")
    check_server("WAF: Path Traversal", make_request(path="/../../etc/passwd"), "403 Forbidden")
    check_server("WAF: Encoded Path Traversal", make_request(path="/%2e%2e/%2e%2e/etc/passwd"), "403 Forbidden")
    check_server("WAF: SQL Injection (%20)", make_request(path="/?q=UNION%20SELECT"), "403 Forbidden")
    check_server("WAF: SQL Injection (+)", make_request(path="/?q=UNION+SELECT"), "403 Forbidden")
    check_server("WAF: XSS", make_request(path="/<script>"), "403 Forbidden")
    check_server("WAF: Missing User-Agent", make_request(user_agent=None), "403 Forbidden")
except ConnectionRefusedError:
    print("[X] The server is not running on 127.0.0.1:8085, start it with: python main.py")