import matplotlib.pyplot as plt
import sys

def parse_cwnd(file_path):
    times = []
    cwnds = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_time = None

    for line in lines:
        line = line.strip()

        if line.isdigit():
            current_time = int(line)
        elif "cwnd:" in line and current_time is not None:
            parts = line.split()
            for part in parts:
                if part.startswith("cwnd:"):
                    cwnd = int(part.split(":")[1])
                    times.append(current_time)
                    cwnds.append(cwnd)
                    break

    return times, cwnds

if len(sys.argv) != 3:
    print("Usage: python plot_cwnd.py <flow1_log.txt> <flow2_log.txt>")
    sys.exit(1)

flow1_path = sys.argv[1]
flow2_path = sys.argv[2]

t1, cwnd1 = parse_cwnd(flow1_path)
t2, cwnd2 = parse_cwnd(flow2_path)

t0 = min(t1[0], t2[0])
t1 = [t - t0 for t in t1]
t2 = [t - t0 for t in t2]

plt.figure(figsize=(10,6))
plt.plot(t1, cwnd1, label='TCP Flow 1')
plt.plot(t2, cwnd2, label='TCP Flow 2')
plt.xlabel("Time (seconds)")
plt.ylabel("Congestion Window (packets)")
plt.title("Change in cwnd (packets) vs Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("cwnd_plot.png")
plt.show()