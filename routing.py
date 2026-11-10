from dijkstra import shortest_path
from ip_utils import ip_to_int, parse_cidr, in_network

GATEWAY = "GateWay"  # the station every request enters from
GRAPH = {}           # station -> {neighbor: cost}
SUBNETS = []         # (network, bits, station): 10.1.0.0/16 C -> (10.1.0.0 as a number, 16, "C")


# Gets the entries of the topology file as (where, words), builds the graph for dijkstra
# every link works in both directions
def build_topology(entries):
    global GRAPH

    graph = {}
    for where, parts in entries:
        if len(parts) != 3:
            raise ValueError(f"{where}: expected STATION_A STATION_B COST")

        a, b, cost_text = parts
        if not cost_text.isdigit() or int(cost_text) == 0:
            raise ValueError(f"{where}: cost must be a positive integer")

        cost = int(cost_text)

        # a station that we meet for the first time gets an empty list of neighbors
        if a not in graph:
            graph[a] = {}
        if b not in graph:
            graph[b] = {}

        graph[a][b] = cost
        graph[b][a] = cost

    if GATEWAY not in graph:
        raise ValueError(f"topology has no links for {GATEWAY}")

    GRAPH = graph
    print(f"[SYSTEM] loaded topology with {len(GRAPH)} stations")


# Gets the entries of the subnets file as (where, words), keeps (network, bits, station)
# needs the topology to be built first
def build_subnets(entries):
    global SUBNETS

    subnets = []
    for where, parts in entries:
        if len(parts) != 2:
            raise ValueError(f"{where}: expected CIDR STATION")

        cidr, station = parts
        if station not in GRAPH:
            raise ValueError(f"{where}: unknown station {station}")

        network, bits = parse_cidr(cidr)
        subnets.append((network, bits, station))

    if not subnets:
        raise ValueError("no subnets found")

    SUBNETS = subnets
    print(f"[SYSTEM] loaded {len(SUBNETS)} subnets")


# Longest prefix match: the most specific network that contains the ip wins
def find_station(ip):
    ip_num = ip_to_int(ip)

    best_station = None
    best_bits = -1
    for network, bits, station in SUBNETS:
        if bits > best_bits and in_network(ip_num, network, bits):
            best_station = station
            best_bits = bits
    return best_station


# The stations from the gateway to the station that hosts the ip, empty list if there is none
def get_route(ip):
    station = find_station(ip)
    if station is None:
        return []  # no network for this ip

    return shortest_path(GRAPH, GATEWAY, station)