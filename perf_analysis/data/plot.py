import numpy as np
import matplotlib.pyplot as plt

# File paths inside test1/ for JSON, XML, and CBOR
folders = ["test1"]
bandwidths = ["1mbit", "5mbit", "10mbit", "50mbit", "100mbit", "500mbit", "1gbit"]

# Function to extract metrics from a file
def extract_metrics(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    requests_sec = None
    for line in lines:
        if 'Requests/sec' in line:
            requests_sec = float(line.split(':')[1].strip())

    return requests_sec

# Initialize dictionaries to store the averages
avg_requests_json = []
avg_requests_xml = []
avg_requests_cbor = []

# Process each bandwidth
for bw in bandwidths:
    json_requests = []
    xml_requests = []
    cbor_requests = []

    for folder in folders:
        # Read JSON results
        json_file = f"{folder}/results_json_{bw}.txt"
        req = extract_metrics(json_file)
        json_requests.append(req)

        # Read XML results
        xml_file = f"{folder}/results_xml_{bw}.txt"
        req = extract_metrics(xml_file)
        xml_requests.append(req)

        # Read CBOR results
        cbor_file = f"{folder}/results_cbor_{bw}.txt"
        req = extract_metrics(cbor_file)
        cbor_requests.append(req)

    # Compute Averages
    avg_requests_json.append(np.mean(json_requests))
    avg_requests_xml.append(np.mean(xml_requests))
    avg_requests_cbor.append(np.mean(cbor_requests))

# Plot the results
x = np.arange(len(bandwidths))
width = 0.2  # Reduced bar width
json_color = 'tab:blue'
xml_color = 'tab:orange'
cbor_color = 'tab:green'

fig, ax = plt.subplots(1, 1, figsize=(12, 6))

# Plot Requests/sec
bars_json = ax.bar(x - width, avg_requests_json, width, label="JSON", color=json_color)
bars_xml = ax.bar(x, avg_requests_xml, width, label="XML", color=xml_color)
bars_cbor = ax.bar(x + width, avg_requests_cbor, width, label="CBOR", color=cbor_color)
ax.set_title("Requests/sec")
ax.set_xticks(x)
ax.set_xticklabels(bandwidths, rotation=45)
ax.set_ylabel("Requests/sec")
ax.legend()

# Annotate each bar with its value
for bar in bars_json:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', color=json_color)

for bar in bars_xml:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', color=xml_color)

for bar in bars_cbor:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', color=cbor_color)

plt.tight_layout()
plt.show()