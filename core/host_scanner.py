import ipaddress

def expand_hosts(ip_range):
    return [str(ip) for ip in ipaddress.ip_network(ip_range, strict=False)]
