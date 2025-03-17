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
    transfer_sec = None
    for line in lines:
        if 'Requests/sec' in line:
            requests_sec = float(line.split(':')[1].strip())
        elif 'Transfer/sec' in line:
            transfer_sec = float(line.split(':')[1].strip().replace('KB', '').strip())

    return requests_sec, transfer_sec

# Initialize dictionaries to store the averages
avg_requests_json = []
avg_transfer_json = []
avg_throughput_json = []

avg_requests_xml = []
avg_transfer_xml = []
avg_throughput_xml = []

avg_requests_cbor = []
avg_transfer_cbor = []
avg_throughput_cbor = []

# Process each bandwidth
for bw in bandwidths:
    json_requests = []
    json_transfer = []
    xml_requests = []
    xml_transfer = []
    cbor_requests = []
    cbor_transfer = []

    for folder in folders:
        # Read JSON results
        json_file = f"{folder}/results_json_{bw}.txt"
        req, trans = extract_metrics(json_file)
        json_requests.append(req)
        json_transfer.append(trans)

        # Read XML results
        xml_file = f"{folder}/results_xml_{bw}.txt"
        req, trans = extract_metrics(xml_file)
        xml_requests.append(req)
        xml_transfer.append(trans)

        # Read CBOR results
        cbor_file = f"{folder}/results_cbor_{bw}.txt"
        req, trans = extract_metrics(cbor_file)
        cbor_requests.append(req)
        cbor_transfer.append(trans)

    # Compute Averages
    avg_requests_json.append(np.mean(json_requests))
    avg_transfer_json.append(np.mean(json_transfer))
    avg_throughput_json.append(np.mean(json_transfer) * 8 / 1000)  # Convert KB/sec to Mbps

    avg_requests_xml.append(np.mean(xml_requests))
    avg_transfer_xml.append(np.mean(xml_transfer))
    avg_throughput_xml.append(np.mean(xml_transfer) * 8 / 1000)  # Convert KB/sec to Mbps

    avg_requests_cbor.append(np.mean(cbor_requests))
    avg_transfer_cbor.append(np.mean(cbor_transfer))
    avg_throughput_cbor.append(np.mean(cbor_transfer) * 8 / 1000)  # Convert KB/sec to Mbps

# Plot the results
x = np.arange(len(bandwidths))
width = 0.2  # Reduced bar width
json_color = 'tab:blue'
xml_color = 'tab:orange'
cbor_color = 'tab:green'

fig, ax = plt.subplots(3, 1, figsize=(12, 18))

for i, (json_metric, xml_metric, cbor_metric, title, ylabel) in enumerate(
    zip([avg_requests_json, avg_transfer_json, avg_throughput_json],
        [avg_requests_xml, avg_transfer_xml, avg_throughput_xml],
        [avg_requests_cbor, avg_transfer_cbor, avg_throughput_cbor],
        ["Requests/sec", "Transfer/sec (KB)", "Throughput (Mbps)"],
        ["Requests/sec", "KB/sec", "Mbps"])
):
    ax[i].bar(x - width, json_metric, width, label="JSON", color=json_color)
    ax[i].bar(x, xml_metric, width, label="XML", color=xml_color)
    ax[i].bar(x + width, cbor_metric, width, label="CBOR", color=cbor_color)
    ax[i].set_title(title)
    ax[i].set_xticks(x)
    ax[i].set_xticklabels(bandwidths, rotation=45)
    ax[i].set_ylabel(ylabel)
    ax[i].legend()

plt.tight_layout()
plt.show()
