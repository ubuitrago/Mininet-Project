from mininet.topo import Topo
from mininet.link import TCLink

class DumbbellTopo(Topo):
    def build(self):

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
        self.addLink(r1, r2, bw=2, delay='50ms', loss=1, use_htb=True)
