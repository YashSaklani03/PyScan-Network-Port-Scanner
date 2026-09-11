import socket
import concurrent.futures


def scan_tcp_port(host, port, timeout=2.0):
    """
    Scan one TCP port.

    Returns:
        (port, state)
        state = open / closed / filtered
    """

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)

            result = sock.connect_ex((host, port))

            if result == 0:
                return port, "open"

            # Connection refused = host reachable, port closed
            if result == 111:
                return port, "closed"

            # Anything else is treated as filtered/no response
            return port, "filtered"

    except socket.timeout:
        return port, "filtered"

    except ConnectionRefusedError:
        return port, "closed"

    except OSError as e:
        if e.errno == 111:
            return port, "closed"
        return port, "filtered"

    except Exception:
        return port, "filtered"


def threaded_tcp_scan(host, ports, workers=100):
    """
    Scan multiple TCP ports concurrently.

    Returns:
        Dictionary:
        {
            port: state
        }
    """

    results = {}

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = {
            executor.submit(scan_tcp_port, host, port): port
            for port in ports
        }

        for future in concurrent.futures.as_completed(futures):
            try:
                port, state = future.result()
                results[port] = state
            except Exception:
                port = futures[future]
                results[port] = "filtered"

    return results
