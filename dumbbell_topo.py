from mininet.topo import Topo
from mininet.link import TCLink

# Constants
PKT_SIZE = 1500  # bytes
BITS_PER_PKT = PKT_SIZE * 8  # 12000 bits
def pms_to_mbps(pms): return (pms * BITS_PER_PKT) / 1e6

class DumbbellTopo(Topo):
    def build(self, one_way_delay=21):
        # Hosts
        h1, h2 = self.addHost('h1'), self.addHost('h2')
        h3, h4 = self.addHost('h3'), self.addHost('h4')

        # Switches (access switches)
        s1, s2 = self.addSwitch('s1'), self.addSwitch('s2')

        # Backbone routers
        r1, r2 = self.addSwitch('r1'), self.addSwitch('r2')

        # Bandwidths in Mbps
        host_bw = pms_to_mbps(80)       # ~0.96 Mbps
        access_bw = pms_to_mbps(21)     # ~0.252 Mbps
        backbone_bw = pms_to_mbps(82)   # ~1 Mbps

        # Delays in ms (assumed per link type)
        # host_delay = "1ms"
        # access_delay = "5ms"
        backbone_delay = f"{one_way_delay}ms"   

        # Buffer = 0.2 * bandwidth (bps) * delay (sec) / bits per packet
        def calc_buffer(bw_mbps, delay_ms):
            bps = bw_mbps * 1e6
            delay_s = int(delay_ms.replace("ms", "")) / 1000
            buffer_bits = 0.2 * bps * delay_s
            return int(buffer_bits / BITS_PER_PKT)

        s1_buf = calc_buffer(access_bw, backbone_delay)
        s2_buf = calc_buffer(access_bw, backbone_delay)

        # Link setup
        for h, s in [(h1, s1), (h2, s1), (h3, s2), (h4, s2)]:
            self.addLink(h, s, bw=host_bw, use_htb=True)

        # Access switch to router
        self.addLink(s1, r1, bw=access_bw, max_queue_size=s1_buf, use_htb=True)
        self.addLink(s2, r2, bw=access_bw, max_queue_size=s2_buf, use_htb=True)

        # Bottleneck link

        self.addLink(r1, r2, bw=backbone_bw, delay=backbone_delay, use_htb=True)
