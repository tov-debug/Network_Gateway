import argparse
from server import start_server
from network_acl import build_blacklist
from routing import build_topology, build_subnets


# Returns the useful lines of a file
def read_entries(filepath):
    entries = []

    with open(filepath, 'r') as f:
        for line_number, line in enumerate(f, start=1):
            text = line.partition('#')[0].strip()

            if text:
                entries.append((f"{filepath}:{line_number}", text.split()))

    return entries


if __name__ == "__main__":
    # connect to command line
    parser = argparse.ArgumentParser(description="Custom HTTP Server & WAF Gateway")
    parser.add_argument('-b', '--blacklist', type=str, default='blacklist.txt', help='Path to the IP ACL blacklist file')
    args = parser.parse_args()

    build_blacklist(read_entries(args.blacklist))
    build_topology(read_entries("topology.txt"))
    build_subnets(read_entries("subnets.txt"))

    print("[SYSTEM] Starting server on port 8085")
    start_server()