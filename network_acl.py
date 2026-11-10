from ip_utils import ip_to_int, parse_cidr, in_network

BLOCKED_SUBNETS = []  # (network, bits, text)


# Gets the entries of the blacklist file 
def build_blacklist(entries):
    global BLOCKED_SUBNETS

    blocked = []
    for where, parts in entries:
        if len(parts) != 1:
            raise ValueError(f"{where}: expected one subnet per line")

        text = parts[0]
        if '/' not in text:
            text += '/32'  # Default to a single IP mask

        network, bits = parse_cidr(text)
        blocked.append((network, bits, text))

    BLOCKED_SUBNETS = blocked
    print(f"[SYSTEM] loaded {len(BLOCKED_SUBNETS)} blocked subnets")


# Checks if a given client IP address falls within any blocked CIDR subnets
def is_blocked(client_ip:str)-> bool:
    ip = ip_to_int(client_ip)

    for network, bits, text in BLOCKED_SUBNETS:
        if in_network(ip, network, bits):
            print(f"[WAF BLOCK] IP {client_ip} blocked by ACL rule {text}")
            return True
        
    return False