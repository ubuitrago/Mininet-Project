#!/usr/bin/env python3

import subprocess
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import tcp_reno
import threading
import time

PERF_DATA = Path("perf.data")
PERF_TRACE = Path("perf_trace.txt")

def run_tcp_workload(cctrl="reno"):
    print(f"Running Congestion Control {cctrl} workload")
    tcp_reno.run()

def run_perf_record(duration=30):
    print(f"Recording perf trace for {duration} seconds...")
    cmd = [
        "sudo", "perf", "record",
        "-e", "tcp:tcp_probe",
        "-a",  # system-wide
        "-o", str(PERF_DATA)
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(duration)
    proc.terminate()
    proc.wait()

def run_perf_script():
    print("Extracting perf script output...")
    # cmd = [
    #     "sudo", "perf", "script",
    #     "--header",
    #     "-F", "comm,pid,tid,cpu,time,event",
    #     "-o", PERF_TRACE
    # ]
    # with open(PERF_TRACE, "w") as out:
    #     subprocess.run(cmd, stdout=out)
    cmd = ["sudo", "perf", "report", "--header"]
    with open(PERF_TRACE, "w") as out:
        subprocess.run(cmd, stdout=out)

def parse_perf_trace(trace_file):
    print("Parsing trace...")
    pattern = re.compile(r'saddr=(\S+) daddr=(\S+) sport=(\d+) dport=(\d+).*cwnd=(\d+).*bytes_acked=(\d+)')
    data = []

    with open(trace_file, 'r') as f:
        for line in f:
            if 'tcp_probe:' in line:
                parts = line.strip().split()
                try:
                    timestamp = float(parts[4].rstrip(':'))
                except (IndexError, ValueError):
                    continue
            elif 'saddr=' in line:
                m = pattern.search(line)
                if m:
                    cwnd = int(m.group(5))
                    acked = int(m.group(6))
                    data.append((timestamp, cwnd, acked))

    df = pd.DataFrame(data, columns=['time', 'cwnd', 'acked'])
    df['time'] -= df['time'].min()
    df['throughput'] = df['acked'].diff() / df['time'].diff()  # bytes/sec
    df.dropna(inplace=True)
    return df

def plot_graphs(df, output_prefix='tcp_reno'):
    print("Plotting graphs...")
    plt.figure(figsize=(10, 5))
    plt.plot(df['time'], df['cwnd'], label='CWND')
    plt.xlabel("Time (s)")
    plt.ylabel("Congestion Window (segments)")
    plt.title("TCP CWND vs Time")
    plt.grid(True)
    plt.legend()
    plt.savefig(f"{output_prefix}_cwnd.png")

    # plt.figure(figsize=(10, 5))
    # plt.plot(df['time'], df['throughput'] / 1024, label='Throughput (KB/s)', color='orange')
    # plt.xlabel("Time (s)")
    # plt.ylabel("Throughput (KB/s)")
    # plt.title("TCP Throughput vs Time")
    # plt.grid(True)
    # plt.legend()
    # plt.savefig(f"{output_prefix}_throughput.png")

    print("Graphs saved as PNGs.")

if __name__ == "__main__":
    duration = 30 
    workload_thread = threading.Thread(target=run_tcp_workload)
    perf_tracing_thread = threading.Thread(target=run_perf_record, args=duration)
    perf_tracing_thread.start()
    time.sleep(2)
    workload_thread.start()
    perf_tracing_thread.join()
    run_perf_script()
    df = parse_perf_trace(PERF_TRACE)
    plot_graphs(df)
