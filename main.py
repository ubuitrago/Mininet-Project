#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

import os
import threading
import subprocess
import sys
import time

class DumbbellTopo(Topo):
    def build(self, delay='21ms'):
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add routers / core switches
        r1 = self.addSwitch('r1')
        r2 = self.addSwitch('r2')

        # Host to switch links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        # Switch to router links
        self.addLink(s1, r1)
        self.addLink(s2, r2)

        # Bottleneck link (introduce delay, low bandwidth here)
        self.addLink(r1, r2, bw=5, delay='50ms', loss=1, use_htb=True)

def log_tcp_info(host, target_ip, output_file, duration):
    cmd = f"while true; do echo $(date +%s) >> {output_file}; ss -ti dst {target_ip} >> {output_file}; sleep 1; done"
    process = subprocess.Popen(cmd, shell=True, executable='/bin/bash', preexec_fn=os.setsid)
    return process

def run(cc_algo, delay, output_file):	
    for suffix in ["_flow1.txt", "_flow2.txt"]:
        path = output_file + suffix
        if os.path.exists(path):
            os.remove(path)	

    topo = DumbbellTopo(delay=delay)

    try:
        net = Mininet(topo=topo, link=TCLink)
    except Exception as e:
        print(f"Error creating mininet: {e}")
        return

    net.start()
    
    h1, h2 = net.get('h1'), net.get('h2')
    h3, h4 = net.get('h3'), net.get('h4')
    # Set congestion control to reno
    h1.cmd(f'sysctl -w net.ipv4.tcp_congestion_control={cc_algo}')
    h3.cmd(f'sysctl -w net.ipv4.tcp_congestion_control={cc_algo}')

    print(f"[+] Setting congestion control algorithm to: {cc_algo}")

    for host in [h1, h2]:
        host.cmd(f'echo {cc_algo} > /proc/sys/net/ipv4/tcp_congestion_control')

    print("[+] Starting flow 1: h1 -> h3 for 2000 seconds")
    #log_thread = threading.Thread(target=log_tcp_info, args=[h1, "10.0.0.3", output_file + "_flow1.txt", 2000])
    log_thread = log_tcp_info(h1, "10.0.0.3", output_file + "_flow1.txt", 2000)
    #log_thread.start()
    h3.cmd('iperf -s -i &')
    h1.cmd(f'iperf -c 10.0.0.3 -t 2000 &')

    print("[*] Waiting 250 seconds before starting flow 2...")
    time.sleep(15)

    print("[+] Starting flow 2: h2 -> h4 for 1750 seconds")
    log_tcp_info(h2, "10.0.0.3", output_file + "_flow2.txt", 1750)
    h4.cmd('iperf -s -i &')
    h2.cmd(f'iperf -c 10.0.0.3 -t 1750 &')

    print("[*] Waiting for test to complete...")
    time.sleep(30)

    print("[+] Stopping network...")
    net.stop()
    log_thread.terminate()

if __name__ == '__main__':
    os.system("mn -c")
    setLogLevel('info')
    if len(sys.argv) != 4:
        print("Usage: sudo ./dumbbell.py <congestion_congrol_algo> <RTT_delay> <output_file>")
        sys.exit(1)

    cc_algo = sys.argv[1]
    delay = sys.argv[2]
    output_file = sys.argv[3]

    run(cc_algo, delay, output_file)