# Converts an IPv4 string (e.g., "192.168.1.1") to a 32-bit integer representation
def ip_to_int(ip):
    parts = ip.split('.')  # array of ip parts
    if len(parts) != 4:
        raise ValueError(f"Bad IPv4 address: {ip}")
    
    for part in parts:
        if not (part.isascii() and part.isdigit()) or int(part) > 255:
            raise ValueError(f"Bad IPv4 address: {ip}")

    num1 = int(parts[0])
    num2 = int(parts[1])
    num3 = int(parts[2])
    num4 = int(parts[3])

    # moving each part to its place:
    res = (num1 << 24) + (num2 << 16) + (num3 << 8) + num4
    return res


# Splits "10.1.0.0/16" to the network as a number and the mask bits
def parse_cidr(text):
    ip_text, slash, bits_text = text.partition('/')
    if not slash or not bits_text.isdigit() or int(bits_text) > 32:
        raise ValueError(f"Bad CIDR: {text}")
    
    return ip_to_int(ip_text), int(bits_text)


# bit mask for comparing ip addresses
def make_mask(bits):
    return (0xFFFFFFFF << (32 - bits)) & 0xFFFFFFFF


# Checks if an ip (as a number) falls inside a network
def in_network(ip, network, bits):
    mask = make_mask(bits)
    return (ip & mask) == (network & mask)