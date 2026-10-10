from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Node, OVSSwitch, RemoteController


def build_topology():
    net = Mininet(
        controller=None,
        link=TCLink,
        switch=OVSSwitch,
        autoSetMacs=True,
        autoStaticArp=False,
    )

    info("*** Adding remote POX controller\n")
    net.addController(
        "c0",
        controller=RemoteController,
        ip="pox",
        port=6633,
    )

    info("*** Adding OpenFlow switches\n")
    s1 = net.addSwitch("s1", protocols="OpenFlow10")
    s2 = net.addSwitch("s2", protocols="OpenFlow10")

    info("*** Adding Linux router\n")
    router = net.addHost("r1", cls=Node, ip="10.0.1.254/24")

    info("*** Adding server-side subnet hosts\n")
    web = net.addHost("hweb", ip="10.0.1.10/24", defaultRoute="via 10.0.1.254")
    gen1 = net.addHost("hgen1", ip="10.0.1.11/24", defaultRoute="via 10.0.1.254")
    gen2 = net.addHost("hgen2", ip="10.0.1.12/24", defaultRoute="via 10.0.1.254")

    info("*** Adding client-side subnet hosts\n")
    client1 = net.addHost("hcli1", ip="10.0.2.10/24", defaultRoute="via 10.0.2.254")
    client2 = net.addHost("hcli2", ip="10.0.2.11/24", defaultRoute="via 10.0.2.254")
    attacker = net.addHost("hatt", ip="10.0.2.200/24", defaultRoute="via 10.0.2.254")

    info("*** Creating links\n")
    for host in (web, gen1, gen2):
        net.addLink(host, s1)

    for host in (client1, client2, attacker):
        net.addLink(host, s2)

    net.addLink(router, s1)
    net.addLink(router, s2)

    info("*** Starting network\n")
    net.start()

    info("*** Configuring router interfaces\n")
    router.cmd("ip addr flush dev r1-eth0")
    router.cmd("ip addr flush dev r1-eth1")
    router.cmd("ip addr add 10.0.1.254/24 dev r1-eth0")
    router.cmd("ip addr add 10.0.2.254/24 dev r1-eth1")
    router.cmd("sysctl -w net.ipv4.ip_forward=1")

    info("*** Testing end-to-end connectivity\n")
    net.pingAll()

    info("*** Mininet CLI ready\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    build_topology()
