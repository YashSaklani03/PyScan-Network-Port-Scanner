#!/usr/bin/env python3
import sys
import time
import socket
from core.tcp_scanner import threaded_tcp_scan
from core.service_detect import detect_service
from core.banner_grabber import grab_banner
from core.vulnerability_checks import basic_vulnerability_checks
from utils.logger import setup_logger

log = setup_logger()
DEFAULT_PORTS = range(1, 10001)

def start_scan(host, ports=None):
    if ports is None:
        ports = DEFAULT_PORTS
    log.info(f"Starting scan on {host}")
    port_states = threaded_tcp_scan(host, ports)
    report = []
    for port in sorted(port_states.keys()):
        state = port_states[port]
        service = detect_service(port)
        banner = None
        if state == "open":
            banner = grab_banner(host, port)
            vulns = basic_vulnerability_checks(port, banner or "")
            log.info(f"Open {port} - {service} - {banner} - {vulns}")
        report.append((host, port, state, service, banner))
    return report

def measure_latency(host, timeout=2):
    try:
        start = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect_ex((host, 80))
        return time.time() - start
    except Exception:
        return None

def print_nmap_style(target, resolved_ip, report, elapsed):
    print(f"\nStarting PyScan at {time.strftime('%Y-%m-%d %H:%M %z')}")
    latency = measure_latency(resolved_ip)
    latency_str = f"({latency:.2f}s latency)" if latency else "(latency unknown)"
    print(f"PyScan scan report for {target} ({resolved_ip})")
    print(f"Host is up {latency_str}.")

    open_rows = [r for r in report if r[2] == "open"]
    closed_rows = [r for r in report if r[2] == "closed"]
    filtered_rows = [r for r in report if r[2] == "filtered"]

    if not open_rows:
        print(f"All {len(report)} scanned ports are filtered or closed.")
    else:
        hidden_count = len(closed_rows) + len(filtered_rows)
        if hidden_count > 0:
            hidden_state = "filtered" if len(filtered_rows) >= len(closed_rows) else "closed"
            print(f"Not shown: {hidden_count} {hidden_state} tcp ports (no-response)")
        print(f"{'PORT':<10}{'STATE':<8}{'SERVICE'}")
        for host, port, state, service, banner in sorted(open_rows, key=lambda r: r[1]):
            port_str = f"{port}/tcp"
            print(f"{port_str:<10}{state:<8}{service}")

    print(f"\nPyScan done: scanned {len(report)} ports in {elapsed:.2f} seconds")

def run_cli():
    target = sys.argv[1]
    if len(sys.argv) == 2:
        ports = DEFAULT_PORTS
    elif len(sys.argv) == 3 and sys.argv[2] == "all":
        ports = range(1, 65536)
    elif len(sys.argv) == 4:
        start_port = int(sys.argv[2])
        end_port = int(sys.argv[3])
        ports = range(start_port, end_port + 1)
    else:
        print("Invalid arguments. Run 'pyscan' with no arguments to launch the GUI.")
        sys.exit(1)

    try:
        resolved_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"Could not resolve host: {target}")
        sys.exit(1)

    start_time = time.time()
    report = start_scan(resolved_ip, ports=ports)
    elapsed = time.time() - start_time
    print_nmap_style(target, resolved_ip, report, elapsed)

def launch_gui():
    from gui.tkinter_gui import run_gui
    run_gui()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        launch_gui()
    else:
        run_cli()
