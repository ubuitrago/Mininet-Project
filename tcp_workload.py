from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from dumbbell_topo import DumbbellTopo
from mininet.log import setLogLevel
import os, time, sys
from typing import Literal

def run_experiment(
    experiment: Literal["exp1", "exp2"] = "exp1",
    one_way_delay_ms=21,
    cctrl: Literal["reno", "cubic", "rtt", "bbr"] = "reno"
):
    """
    Runs TCP experiment with configurable flow timing and congestion control.
    - exp1: flow2 starts 250s later
    - exp2: both flows start simultaneously
    """
    topo = DumbbellTopo(delay=one_way_delay_ms)
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')

    # Set all hosts to use selected congestion control
    for h in (h1, h2, h3, h4):
        h.cmd(f"sysctl -w net.ipv4.tcp_congestion_control={cctrl}")

    print(f"[{cctrl.upper()}] One-way delay set to {one_way_delay_ms}ms on bottleneck link")

    # Start servers
    h3.cmd("iperf3 -s -i 1 -p 5001 > h3_server.txt &")
    h4.cmd("iperf3 -s -i 1 -p 5001 > h4_server.txt &")

    # Start flow 1 (immediate)
    h1.cmd(f"iperf3 -V -4 -i 1 -f m -c {h3.IP()} -t 2000 -p 5001 > h1_client.txt &")

    if experiment == "exp1":
        print("[exp1] Starting flow2 with 250s delay")
        time.sleep(250)
        h2.cmd(f"iperf3 -V -4 -i 1 -f m -c {h4.IP()} -t 1750 -p 5001 > h2_client.txt")
    elif experiment == "exp2":
        print("[exp2] Starting flow2 immediately")
        h2.cmd(f"iperf3 -V -4 -i 1 -f m -c {h4.IP()} -t 2000 -p 5001 > h2_client.txt")
    # NOTE: We run flow 2 in the foreground ALWAYS, if not the log output will be interrupted by net.stop()
    print("[+] Stopping network...")
    net.stop()
    os.system("mn -c > /dev/null")


# if __name__ == "__main__":
#     setLogLevel("info")
#     if len(sys.argv) < 3:
#         run(21)  # default delay
#     else:
#          run(sys.argv[2])
