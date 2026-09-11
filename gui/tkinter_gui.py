import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import time
import socket
from main import start_scan


def run_gui():
    root = tk.Tk()
    root.title("PyScan - Network Port Scanner")
    root.geometry("650x640")

    tk.Label(root, text="Target Host / IP:", font=("Arial", 10, "bold")).pack(pady=(15, 0))
    entry = tk.Entry(root, width=45)
    entry.pack(pady=5)

    mode_frame = tk.Frame(root)
    mode_frame.pack(pady=5)
    scan_mode = tk.StringVar(value="default")
    tk.Radiobutton(mode_frame, text="Top 10000 ports (default)", variable=scan_mode, value="default").pack(anchor="w")
    tk.Radiobutton(mode_frame, text="All ports (1-65535)", variable=scan_mode, value="all").pack(anchor="w")

    range_frame = tk.Frame(mode_frame)
    tk.Radiobutton(range_frame, text="Custom range:", variable=scan_mode, value="custom").pack(side="left")
    start_entry = tk.Entry(range_frame, width=8)
    start_entry.pack(side="left", padx=5)
    tk.Label(range_frame, text="to").pack(side="left")
    end_entry = tk.Entry(range_frame, width=8)
    end_entry.pack(side="left", padx=5)
    range_frame.pack(anchor="w", pady=3)

    progress = ttk.Progressbar(root, mode="indeterminate", length=500)
    progress.pack(pady=10)

    status_label = tk.Label(root, text="Ready.", fg="gray")
    status_label.pack()

    output_box = scrolledtext.ScrolledText(root, width=75, height=18, font=("Consolas", 10))
    output_box.pack(pady=10, padx=10)

    scan_button = tk.Button(root, text="Start Scan", font=("Arial", 14, "bold"), bg="#2e7d32", fg="white", width=20, height=2)
    scan_button.pack(pady=10)

    def get_ports():
        mode = scan_mode.get()
        if mode == "default":
            return range(1, 10001), "top 10000 ports"
        elif mode == "all":
            return range(1, 65536), "all ports (1-65535)"
        else:
            try:
                s = int(start_entry.get())
                e = int(end_entry.get())
                if s < 1 or e > 65535 or s > e:
                    return None, None
                return range(s, e + 1), f"{s}-{e}"
            except ValueError:
                return None, None

    def finish_with_error(message):
        def update():
            progress.stop()
            output_box.insert(tk.END, f"\n{message}\n")
            status_label.config(text="Scan failed.", fg="red")
            scan_button.config(state="normal", text="Start Scan")
        root.after(0, update)

    def finish_with_results(target, resolved_ip, label, report, elapsed):
        def update():
            progress.stop()
            open_rows = []
            closed_count = 0
            filtered_count = 0
            for row in report:
                _host, port, state, service, banner = row
                if state == "open":
                    open_rows.append((port, service, banner))
                elif state == "closed":
                    closed_count += 1
                else:
                    filtered_count += 1

            output_box.insert(tk.END, f"\nScan report for {target} ({resolved_ip})\n")
            output_box.insert(tk.END, f"Scanned range: {label}\n")

            if not open_rows:
                output_box.insert(tk.END, f"No open ports found. ({closed_count} closed, {filtered_count} filtered)\n")
            else:
                hidden_count = closed_count + filtered_count
                if hidden_count > 0:
                    output_box.insert(tk.END, f"Not shown: {hidden_count} filtered/closed tcp ports (no-response)\n")
                output_box.insert(tk.END, f"{'PORT':<10}{'STATE':<8}{'SERVICE'}\n")
                output_box.insert(tk.END, "-" * 45 + "\n")
                for port, service, banner in sorted(open_rows, key=lambda r: r[0]):
                    port_str = f"{port}/tcp"
                    banner_str = f"  {banner}" if banner else ""
                    output_box.insert(tk.END, f"{port_str:<10}{'open':<8}{service}{banner_str}\n")

            output_box.insert(tk.END, f"\nScan done: {len(open_rows)} open port(s) found\n")
            output_box.insert(tk.END, f"Scanned in {elapsed:.2f} seconds\n")
            output_box.see(tk.END)
            status_label.config(text="Scan complete.", fg="green")
            scan_button.config(state="normal", text="Start Scan")
        root.after(0, update)

    def do_scan(target, ports, label):
        try:
            resolved_ip = socket.gethostbyname(target)
        except socket.gaierror:
            finish_with_error(f"Could not resolve host: {target}")
            return
        try:
            start_time = time.time()
            report = start_scan(resolved_ip, ports=ports)
            elapsed = time.time() - start_time
        except Exception as e:
            finish_with_error(f"ERROR during scan: {e}")
            return
        finish_with_results(target, resolved_ip, label, report, elapsed)

    def on_scan():
        target = entry.get().strip()
        if not target:
            status_label.config(text="Please enter a target host.", fg="red")
            return
        ports, label = get_ports()
        if ports is None:
            status_label.config(text="Invalid custom port range.", fg="red")
            return
        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, f"Scanning {target} ({label})...\n")
        status_label.config(text="Scanning... please wait.", fg="orange")
        scan_button.config(state="disabled", text="Scanning...")
        progress.start(10)
        thread = threading.Thread(target=do_scan, args=(target, ports, label), daemon=True)
        thread.start()

    scan_button.config(command=on_scan)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
