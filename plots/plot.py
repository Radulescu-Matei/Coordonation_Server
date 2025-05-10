import os
import pandas as pd
import matplotlib.pyplot as plt
import re

# Directory with your data files
data_dir = "./"  # adjust if needed
output_dir = os.path.join(data_dir, "plots")
os.makedirs(output_dir, exist_ok=True)

# Collect all response time files (no extension required)
all_files = [f for f in os.listdir(data_dir) if f.startswith("response_times_")]

# === Plot 1: Average response time vs number of vehicles (30 requests) ===
vehicles_30 = [f for f in all_files if "30requests" in f]
vehicle_avg_times = []

for file in vehicles_30:
    match = re.search(r"response_times_(\d+)vehicles_30requests", file)
    if match:
        num_vehicles = int(match.group(1))
        df = pd.read_csv(os.path.join(data_dir, file))
        avg_time = df["response_time"].mean()
        vehicle_avg_times.append((num_vehicles, avg_time))

if vehicle_avg_times:
    vehicle_avg_times.sort()
    x1, y1 = zip(*vehicle_avg_times)
    plt.figure()
    plt.plot(x1, y1, marker='o')
    plt.title("Average Response Time vs Number of Vehicles (30 requests)")
    plt.xlabel("Number of Vehicles")
    plt.ylabel("Average Response Time (s)")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "avg_response_vs_vehicles.png"))
    plt.close()
else:
    print("⚠️ No valid files found for 30 requests plot.")

# === Plot 2: Average response time vs number of requests (3 vehicles) ===
requests_3vehicles = [f for f in all_files if "3vehicles" in f]
requests_avg_times = []

for file in requests_3vehicles:
    match = re.search(r"response_times_3vehicles_(\d+)requests", file)
    if match:
        num_requests = int(match.group(1))
        df = pd.read_csv(os.path.join(data_dir, file))
        avg_time = df["response_time"].mean()
        requests_avg_times.append((num_requests, avg_time))

if requests_avg_times:
    requests_avg_times.sort()
    x2, y2 = zip(*requests_avg_times)
    plt.figure()
    plt.plot(x2, y2, marker='o', color='orange')
    plt.title("Average Response Time vs Number of Requests (3 vehicles)")
    plt.xlabel("Number of Requests")
    plt.ylabel("Average Response Time (s)")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "avg_response_vs_requests_3vehicles.png"))
    plt.close()
else:
    print("⚠️ No valid files found for 3 vehicles request plot.")

# === Plot 3: Response time per vehicle (8 vehicles, 30 requests) ===
file_8vehicles = "response_times_8vehicles_30requests"
if file_8vehicles in all_files:
    df_8 = pd.read_csv(os.path.join(data_dir, file_8vehicles))
    plt.figure()
    for vid in sorted(df_8["vehicle_id"].unique()):
        plt.plot(df_8[df_8["vehicle_id"] == vid]["response_time"].values, label=f"Vehicle {vid}")
    plt.title("Response Time per Vehicle (8 vehicles, 30 requests)")
    plt.xlabel("Request Index")
    plt.ylabel("Response Time (s)")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "response_per_vehicle_8vehicles.png"))
    plt.close()
else:
    print(f"⚠️ File {file_8vehicles} not found.")

# === Plot 4: Response time per vehicle (3 vehicles, 90 requests) ===
file_3v_90r = "response_times_3vehicles_90requests"
if file_3v_90r in all_files:
    df_3v_90 = pd.read_csv(os.path.join(data_dir, file_3v_90r))
    plt.figure()
    for vid in sorted(df_3v_90["vehicle_id"].unique()):
        plt.plot(df_3v_90[df_3v_90["vehicle_id"] == vid]["response_time"].values, label=f"Vehicle {vid}")
    plt.title("Response Time per Vehicle (3 vehicles, 90 requests)")
    plt.xlabel("Request Index")
    plt.ylabel("Response Time (s)")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "response_per_vehicle_3vehicles_90requests.png"))
    plt.close()
else:
    print(f"⚠️ File {file_3v_90r} not found.")
