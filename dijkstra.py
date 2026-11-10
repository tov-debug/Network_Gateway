import heapq


def check_graph(graph, start, destination):
    # all the errors live here
    if start not in graph:
        raise ValueError("Unknown start: " + str(start))
    
    if destination not in graph:
        raise ValueError("Unknown destination: " + str(destination))

    for u in graph:
        for v, w in graph[u].items():
            if v not in graph:
                raise ValueError("Unknown node in link from " + str(u) + " to " + str(v))
            
            if w < 0:  # dijkstra can't work with negative weights
                raise ValueError("Negative weight from " + str(u) + " to " + str(v))


def build_path(prev, start, destination):
    path = []
    node = destination
    while node != start:
        path.append(node)
        node = prev[node]
    path.append(start)
    path.reverse()
    return path


def shortest_path(graph, start, destination):
    check_graph(graph, start, destination)

    dist = {}
    prev = {}
    for v in graph:
        dist[v] = float("inf")
    dist[start] = 0

    q = [(0, start)]

    while q:
        d, u = heapq.heappop(q)
        if d > dist[u]:  # old entry, we already found a shorter way to u
            continue
        if u == destination:
            break

        for v, w in graph[u].items():
            if dist[u] + w < dist[v]:  # a shorter path to v has been discovered
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(q, (dist[v], v))

    if dist[destination] == float("inf"):
        return []  # no route

    return build_path(prev, start, destination)