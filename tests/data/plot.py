import numpy as np
import matplotlib.pyplot as plt

# File names corresponding to each bandwidth for JSON and XML
json_file_names = [
    'results_json_1mbit.txt', 'results_json_5mbit.txt', 'results_json_10mbit.txt',
    'results_json_50mbit.txt', 'results_json_100mbit.txt', 'results_json_500mbit.txt', 'results_json_1gbit.txt'
]
xml_file_names = [
    'results_xml_1mbit.txt', 'results_xml_5mbit.txt', 'results_xml_10mbit.txt',
    'results_xml_50mbit.txt', 'results_xml_100mbit.txt', 'results_xml_500mbit.txt', 'results_xml_1gbit.txt'
]

# Function to extract the relevant metrics (Requests/sec, Transfer/sec)
def extract_metrics(file_name):
    with open(file_name, 'r') as file:
        lines = file.readlines()

    requests_sec = None
    transfer_sec = None
    # Search for the metrics in the file content
    for line in lines:
        if 'Requests/sec' in line:
            requests_sec = float(line.split(':')[1].strip())
        elif 'Transfer/sec' in line:
            transfer_sec = float(line.split(':')[1].strip().replace('KB', '').strip())
        
    return requests_sec, transfer_sec

# Initialize lists to hold extracted data
requests_sec_json = []
transfer_sec_kb_json = []
throughput_mbps_json = []

requests_sec_xml = []
transfer_sec_kb_xml = []
throughput_mbps_xml = []

# Extract data from each JSON file
for file_name in json_file_names:
    req_sec, transf_sec = extract_metrics(file_name)
    requests_sec_json.append(req_sec)
    transfer_sec_kb_json.append(transf_sec)
    throughput_mbps_json.append(transf_sec * 8 / 1000)  # Convert KB/sec to Mbps

# Extract data from each XML file
for file_name in xml_file_names:
    req_sec, transf_sec = extract_metrics(file_name)
    requests_sec_xml.append(req_sec)
    transfer_sec_kb_xml.append(transf_sec)
    throughput_mbps_xml.append(transf_sec * 8 / 1000)  # Convert KB/sec to Mbps

# Bandwidth labels
bandwidths = ["1mbit", "5mbit", "10mbit", "50mbit", "100mbit", "500mbit","1gbit"]

# Prepare the data for plotting
x = np.arange(len(bandwidths))  # Bandwidth index
width = 0.35  # Bar width

# Colors for JSON and XML
json_color = 'tab:blue'
xml_color = 'tab:orange'

# Plot Requests/sec, Transfer/sec, and Throughput
fig, ax = plt.subplots(3, 1, figsize=(12, 18))

for i, (json_metric, xml_metric, title, ylabel) in enumerate(
    zip([requests_sec_json, transfer_sec_kb_json, throughput_mbps_json],
        [requests_sec_xml, transfer_sec_kb_xml, throughput_mbps_xml],
        ["Requests/sec", "Transfer/sec (KB)", "Throughput (Mbps)"],
        ["Requests/sec", "KB/sec", "Mbps"])
):
    ax[i].bar(x - width / 2, json_metric, width, label="JSON", color=json_color)
    ax[i].bar(x + width / 2, xml_metric, width, label="XML", color=xml_color)
    ax[i].set_title(title)
    ax[i].set_xticks(x)
    ax[i].set_xticklabels(bandwidths, rotation=45)
    ax[i].set_ylabel(ylabel)
    ax[i].legend()

plt.tight_layout()
plt.show()
