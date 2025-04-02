#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

import os
import sys
import time

class DumbbellTopo(Topo):
	def build(self, delay='21ms'):
		h1 = self.addHost('h1')
		h2 = self.addHost('h2')
		h3 = self.addHost('h3')
		h4 = self.addHost('h4')
		
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2')

		r1 = self.addSwitch('r1')
		r2 = self.addSwitch('r2')

		self.addLink(h1, s1, bw=2.6)
		self.addLink(h2, s1, bw=2.6)
		self.addLink(h3, s2, bw=2.6)
		self.addLink(h4, s2, bw=2.6)

		buffer = calculate_queue_size(2.6, delay)
		print(f'Buffer size: {buffer}')
		self.addLink(s1, r1, bw=2.6, max_queue_size=buffer)
		self.addLink(s2, r2, bw=2.6, max_queue_size=buffer)

		self.addLink(r1, r2, bw=10.2, delay=delay)

def log_tcp_info(host, target_ip, output_file):
	cmd = f"while true; do echo $(date +%s) >> {output_file}; ss -ti dst {target_ip} >> {output_file}; sleep 1; done"
	host.cmd(f'{cmd} &')

def calculate_queue_size(bw_mbps, delay_str, packet_size_bits=12000, buffer_fraction=0.2):
	delay_ms = int(''.join(filter(str.isdigit, delay_str)))
	delay_sec = delay_ms / 1000.0
	bw_bps = bw_mbps * 1_000_000

	buffer_bits = buffer_fraction * bw_bps * delay_sec
	queue_size_packets = int(buffer_bits / packet_size_bits)
	return max(queue_size_packets, 1)

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

	print(f"[+] Setting congestion control algorithm to: {cc_algo}")
	h1, h2 = net.get('h1'), net.get('h2')
	h3, h4 = net.get('h3'), net.get('h4')
	h1.cmd(f'sysctl -w net.ipv4.tcp_congestion_control=reno')
	h2.cmd(f'sysctl -w net.ipv4.tcp_congestion_control=reno')
	

	print("[+] Starting flow 1: h1 -> h3 for 2000 seconds")
	log_tcp_info(h1, h3.IP(), output_file + "_flow1.txt")
	h3.cmd('iperf -s -i 1 &')
	h1.cmd(f'iperf -c {h3.IP()} -t 2000 &')

	print("[*] Waiting 250 seconds before starting flow 2...")
	time.sleep(30)

	print("[+] Starting flow 2: h2 -> h4 for 1750 seconds")
	log_tcp_info(h2, h4.IP(), output_file + "_flow2.txt")
	h4.cmd('iperf -s -i 1 &')
	h2.cmd(f'iperf -c {h4.IP()} -t 1750 &')

	print("[*] Waiting for test to complete...")
	time.sleep(90)

	print("[+] Stopping network...")
	net.stop()

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
