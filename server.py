import socket
from waf import inspect_request
from network_acl import is_blocked
from ip_utils import ip_to_int
from routing import find_station, get_route


# Parses raw HTTP request data into HTTP method, path, protocol version, and headers dictionary
def parse_request(data):
    str_data = data.decode('utf-8', errors= 'ignore')
    request_line , separator, rest = str_data.partition('\r\n') 

    parts = request_line.split(' ')
    if not separator or len(parts) != 3:
        raise ValueError("Malformed request line")
    request_type, path, client_proto = parts

    headers_lines = rest.split('\r\n')

    headers = {}
    for line in headers_lines:
        if not line:
            break

        name, separator, value = line.partition(':')
        if not separator:
            raise ValueError("Malformed header line")
        value = value.strip()
        headers[name.lower()] = value
    
    return request_type,path, client_proto, headers


# Gets and validates the destination IP from the request headers
def get_destination(headers):
    ip = headers.get("x-destination-ip")
    if ip is None:
        raise ValueError("Missing X-Destination-IP header")

    ip_to_int(ip)  # raises ValueError if the ip is not valid
    return ip


# Constructs a basic HTTP/1.1 response string with Content-Length and encodes it to UTF-8
def build_response(status, body):
    
    server_proto = "HTTP/1.1"
    length = len(body.encode('utf-8'))
    response = server_proto + " " + status + "\r\nContent-Length: " + str(length) + "\r\n\r\n" + body
    res = response.encode('utf-8')

    return res


# Builds a response and sends it to the client
def reply(client_sock, status, body):
    res = build_response(status, body)
    client_sock.send(res)


# Handles an incoming client connection: verifies IP against ACL, inspects HTTP payload with WAF,
# finds the route to the destination and returns response
def handle_client(client_sock, client_ip):
    data = client_sock.recv(1024)
    if not data:
        return
    
    if is_blocked(client_ip):
        reply(client_sock, "403 Forbidden", "<h1>403 Forbidden - IP Blocked by WAF</h1>")
        return

    try:
        request_type, path, client_proto, headers = parse_request(data)
    except ValueError:
        reply(client_sock, "400 Bad Request", "<h1>400 Bad Request</h1>")
        return

    allowed = inspect_request(path, headers)
    if not allowed:
        reply(client_sock, "403 Forbidden", "<h1>403 Forbidden - Request Blocked by WAF</h1>")
        return

    try:
        destination = get_destination(headers)
    except ValueError:
        reply(client_sock, "400 Bad Request", "<h1>400 Bad Request - Invalid destination IP</h1>")
        return

    station = find_station(destination)
    if station is None:
        reply(client_sock, "404 Not Found", "<h1>404 Not Found - Destination subnet not mapped</h1>")
        return

    route = get_route(destination)
    if not route:
        reply(client_sock, "502 Bad Gateway", "<h1>502 Bad Gateway - No route to destination station</h1>")
        return

    for i in range(len(route) - 1):
        print(f"[ROUTE] {route[i]} -> {route[i + 1]}")

    route_text = " -> ".join(route)
    body = f"<h1>200 OK - Destination reached</h1><p>Route: {route_text}</p>"
    reply(client_sock, "200 OK", body)
    return

# Initializes and runs the TCP socket server on port 8085 (all interfaces, inside Docker the port is published to localhost only)
def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # lets us restart right away
    server_sock.bind(('0.0.0.0', 8085 ))
    server_sock.listen(1)

    while True:
        client_sock, client_add = server_sock.accept()
        client_ip = client_add[0] # the ip address of this client
        client_sock.settimeout(5)  # a silent client can't block the whole server
        try:
            handle_client(client_sock, client_ip)
        except Exception as e:
            print(f"[ERROR] Failed to handle client: {e}")
        finally:
            client_sock.close()