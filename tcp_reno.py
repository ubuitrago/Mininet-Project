from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
from dumbbell_topo import DumbbellTopo

def run():
    topo = DumbbellTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    h1, h3 = net.get('h1', 'h3')

    # Set congestion control to reno
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=reno')
    h3.cmd('sysctl -w net.ipv4.tcp_congestion_control=reno')

    # Start iperf server on h3
    h3.cmd('iperf -s -i 1 > server_reno.txt &')

    # Start iperf client on h1
    print(h1.cmd('iperf -c 10.0.0.3 -t 10 -i 1 > client_reno.txt'))

    # CLI(net)
    net.stop()

# if __name__ == '__main__':
#     setLogLevel('info')
#     run()
