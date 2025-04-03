from mininet.topo import Topo
from mininet.link import TCLink

# Constants
PKT_SIZE = 1500  # bytes
BITS_PER_PKT = PKT_SIZE * 8  # 12000 bits
def pms_to_mbps(pms): return (pms * BITS_PER_PKT) / 1000

class DumbbellTopo(Topo):
    def build(self, delay=21):
        # Hosts
        h1, h2 = self.addHost('h1'), self.addHost('h2')
        h3, h4 = self.addHost('h3'), self.addHost('h4')

        # Switches (access switches)
        s1, s2 = self.addSwitch('s1'), self.addSwitch('s2')

        # Backbone routers
        r1, r2 = self.addSwitch('r1'), self.addSwitch('r2')

        # Bandwidths in Mbps
        host_bw = pms_to_mbps(80)       # 960 Mbps
        access_bw = pms_to_mbps(21)     # 252 Mbps
        backbone_bw = pms_to_mbps(82)   # ~1 Mbps
  
        # Max_queue_size
        host_buf = 80*delay
        sbuf = (21*delay*20)/100
        backbone_buf = 82*delay
        
        # Link setup
        for h, s in [(h1, s1), (h2, s1), (h3, s2), (h4, s2)]:
            self.addLink(h, s, cls=TCLink, bw=host_bw, max_queue_size=host_buf, use_htb=True)

        # Access switch to router
        self.addLink(s1, r1, cls=TCLink, delay='0ms', bw=access_bw, max_queue_size=sbuf, use_htb=True)
        self.addLink(s2, r2, cls=TCLink, delay='0ms', bw=access_bw, max_queue_size=sbuf, use_htb=True)

        # Bottleneck link
        self.addLink(r1, r2, cls=TCLink, bw=backbone_bw, delay=backbone_delay, max_queue_size=backbone_buf , use_htb=True)
