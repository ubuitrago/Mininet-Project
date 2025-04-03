from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
from dumbbell_topo import DumbbellTopo
from mininet.log import setLogLevel
import os, time

def log_tcp_info(host, target_ip, output_file):
	cmd = f"while true; do echo $(date +%s) >> {output_file}; ss -ti dst {target_ip} >> {output_file}; sleep 1; done"
	host.cmd(f'{cmd} &')
     
def run(one_way_delay_ms=21):
    """
    Launch Mininet with TCP Reno and custom one-way delay on the backbone (r1<->r2).
    one_way_delay_ms: int – one-way delay in milliseconds (e.g., 21, 81, 162)
    """
    topo = DumbbellTopo(one_way_delay=one_way_delay_ms)
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    h1, h2, h3, h4 = net.get('h1', 'h2', 'h3', 'h4')

    # Set all hosts to use TCP Reno
    for h in (h1, h2, h3, h4):
        h.cmd("sysctl -w net.ipv4.tcp_congestion_control=reno")

    print(f"[TCP Reno] One-way delay set to {one_way_delay_ms}ms on bottleneck link")

    # Start iperf servers
    h3.cmd("iperf -s -i 1 > h3_server.txt &")
    h4.cmd("iperf -s -i 1 > h4_server.txt &")

    # Start first flow: h1 → h3
    output_file = "tcp_reno"
    log_tcp_info(h1, h3.IP(), output_file + "_flow1.txt")
    h1.cmd(f"iperf -c {h3.IP()} -t 2000 -i 1 > h1_client.txt &")

    # Start second flow: h2 → h4 (delayed start)
    log_tcp_info(h2, h4.IP(), output_file + "_flow2.txt")
    h2.cmd(f"sleep 250; iperf -c {h4.IP()} -t 1750 -i 1 > h2_client.txt &")

    print("[+] Stopping network...")
    net.stop()
    os.system("mn -c")

if __name__ == "__main__":
    setLogLevel("info")
    run(21)  # default delay
