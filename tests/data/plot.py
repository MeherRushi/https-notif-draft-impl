import numpy as np
import matplotlib.pyplot as plt

# File names corresponding to each bandwidth
file_names = [
    'results_json_1mbit.txt', 'results_xml_1mbit.txt',
    'results_json_5mbit.txt', 'results_xml_5mbit.txt',
    'results_json_10mbit.txt', 'results_xml_10mbit.txt',
    'results_json_50mbit.txt', 'results_xml_50mbit.txt',
    'results_json_100mbit.txt', 'results_xml_100mbit.txt',
    'results_json_1gbit.txt', 'results_xml_1gbit.txt'
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
requests_sec = []
transfer_sec_kb = []
throughput_mbps = []  # We will calculate this from transfer/sec for simplicity

# Extract data from each file
for file_name in file_names:
    req_sec, transf_sec = extract_metrics(file_name)
    requests_sec.append(req_sec)
    transfer_sec_kb.append(transf_sec)
    throughput_mbps.append(transf_sec * 8 / 1000)  # Convert KB/sec to Mbps

# Bandwidth labels
bandwidths = ["1mbit", "5mbit", "10mbit", "50mbit", "100mbit", "500mbit", "1gbit"]

# Prepare the data for plotting
x = np.arange(len(bandwidths))  # Bandwidth index
width = 0.35  # Bar width

# Plot Requests/sec, Transfer/sec, and Throughput
fig, ax = plt.subplots(3, 1, figsize=(12, 18))

for i, metric, title, ylabel in zip(
    range(3),
    [requests_sec, transfer_sec_kb, throughput_mbps],
    ["Requests/sec", "Transfer/sec (KB)", "Throughput (Mbps)"],
    ["Requests/sec", "KB/sec", "Mbps"]
):
    ax[i].bar(x - width / 2, [metric[j] for j in range(len(bandwidths))], width, label="JSON/XML Data")
    ax[i].set_title(title)
    ax[i].set_xticks(x)
    ax[i].set_xticklabels(bandwidths, rotation=45)
    ax[i].set_ylabel(ylabel)
    ax[i].legend()

plt.tight_layout()
plt.show()
