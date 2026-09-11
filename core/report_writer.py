import json
import csv

def save_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def save_csv(data, file):
    with open(file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Host", "Port", "Service", "Banner"])
        for row in data:
            writer.writerow(row)


def save_html(data, file):
    with open(file, "w") as f:
        f.write("<html><body><h1>Scan Report</h1><table border='1'>")
        f.write("<tr><th>Host</th><th>Port</th><th>Service</th><th>Banner</th></tr>")
        for row in data:
            f.write(f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>")
        f.write("</table></body></html>")
