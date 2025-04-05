#!/usr/bin/env python3

import re
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import shutil
from tcp_workload import run_experiment
import threading
import argparse

def cleanup(experiment: str, delay: int, cctrl: str):
    """
    Renames and moves experiment log files to /tmp with metadata included in filenames.
    """
    log_files = ["h1_client.txt", "h2_client.txt", "h3_server.txt", "h4_server.txt"]

    for file in log_files:
        src = Path(file)
        if src.exists():
            # New filename with parameters
            renamed = f"{src.stem}_exp{experiment}_delay{delay}_cctrl{cctrl}{src.suffix}"
            dst = Path("/tmp") / renamed

            # Move file
            shutil.move(str(src), dst)
            print(f"Moved {file} → {dst}")
        else:
            print(f"Skipped missing: {file}")

    print("Cleanup and archive complete.")

def run_tcp_workload(experiment:str, delay:int, cctrl:str):
    print(f"Running Congestion Control {cctrl} workload")
    run_experiment(experiment=experiment, one_way_delay_ms=delay, cctrl=cctrl)
    
def parse_iperf_bit_trace(file_path, mss_bytes=1448):
    print("Parsing iperf3 throughput trace...")
    pattern = re.compile(r'\[\s*\d+\]\s+([\d\.]+)-[\d\.]+\s+sec\s+[\d\.]+\s+MBytes\s+([\d\.]+)\s+Mbits/sec\s+\d+\s+(\d+)\s+KBytes')
    times = []
    bitrate = []

    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                time_sec = float(match.group(1))
                times.append(time_sec)
                mbytes = float(match.group(2))
                bitrate.append(mbytes)

    df = pd.DataFrame({'time': times, 'bitrate': bitrate})
    return df

def parse_iperf_cwnd_trace(file_path, mss_bytes=1448):
    print("Parsing iperf3 cwnd trace...")
    pattern = re.compile(r'\[\s*\d+\]\s+([\d\.]+)-[\d\.]+\s+sec\s+[\d\.]+\s+MBytes\s+[\d\.]+\s+Mbits/sec\s+\d+\s+(\d+)\s+KBytes')
    times = []
    cwnd_packets = []

    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                time_sec = float(match.group(1))
                cwnd_kb = int(match.group(2))
                cwnd_bytes = cwnd_kb * 1024
                cwnd_pkts = cwnd_bytes / mss_bytes
                times.append(time_sec)
                cwnd_packets.append(cwnd_pkts)

    df = pd.DataFrame({'time': times, 'cwnd_packets': cwnd_packets})
    return df

def plot_exp(flow_1:pd.DataFrame, flow_2:pd.DataFrame, title="CWND over Time", output="cwnd_vs_time.png"):
    print(f"Plotting {title}...")
    plt.figure(figsize=(10, 5))
    if "throughput" in output:
        # Flow 1
        plt.plot(flow_1['time'], flow_1['bitrate'], color='black', label='Flow 1 (h1 → h3)')

        # Flow 2
        plt.plot(flow_2['time'], flow_2['bitrate'], color='orange', label='Flow 2 (h2 → h4)')
        plt.ylabel("Throughput (Mbps)")

    else:
        # Flow 1
        plt.plot(flow_1['time'], flow_1['cwnd_packets'], color='red', label='Flow 1 (h1 → h3)')
        # Flow 2: Blue, shifted by 250s
        plt.plot(flow_2['time'] + 250, flow_2['cwnd_packets'], color='blue', label='Flow 2 (h2 → h4)')
        plt.ylabel("Congestion Window (packets)")
    # Formatting
    plt.xlabel("Time (s)")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig(output)
    plt.show()
    print(f"Plot saved to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run TCP workload with specified parameters.")
    parser.add_argument("--experiment", type=str, default="exp1", help="Experiment type (exp1 or exp2)")
    parser.add_argument("--delay", type=int, default=21, help="One-way delay in ms")
    parser.add_argument("--cctrl", type=str, default="reno", help="Congestion control algorithm (reno, cubic, rtt, bbr)")
    args = parser.parse_args()

    # Cleanup
    print("Cleaning up any old log files...")
    cleanup(args.experiment, args.delay, args.cctrl)
    # Start workload & perf script
    workload_thread = threading.Thread(target=run_tcp_workload, args=(args.experiment, args.delay, args.cctrl))
    workload_thread.start()
    # Wait for workload to complete
    workload_thread.join()

    # Extract and plot CWND
    if args.experiment == "exp1":
        h1_df = parse_iperf_cwnd_trace("h1_client.txt")
        h2_df = parse_iperf_cwnd_trace("h2_client.txt")
    elif args.experiment == "exp2":
        h1_df = parse_iperf_bit_trace("h1_client.txt")
        h2_df = parse_iperf_bit_trace("h2_client.txt")
    # Automatically generate the output filename based on parameters
    if args.experiment == "exp1":
        output_filename = f"{args.cctrl}_{args.delay}_cwnd.png"
    elif args.experiment == "exp2":
        output_filename = f"{args.cctrl}_{args.delay}_throughput.png"
    # Generate Plots and save
    plot_exp(flow_1 = h1_df, flow_2 = h2_df, title = f"{args.cctrl.upper()} - {args.delay}ms Delay", output=output_filename)

    print("Experiment completed.")
    # NOTE: The script will automatically generate the output filename based on the parameters provided.
