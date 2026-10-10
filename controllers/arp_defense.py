from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet

log = core.getLogger()

valid_arp = {}
blacklist = set()


class ARPDefense(object):
    def __init__(self):
        core.openflow.addListeners(self)
        log.info("ARP defense module loaded")

    def _handle_ConnectionUp(self, event):
        log.info("Switch connected: %s", event.connection)

        flow = of.ofp_flow_mod()
        flow.priority = 50000
        flow.match.dl_type = ethernet.ARP_TYPE
        flow.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
        event.connection.send(flow)

        log.info("ARP inspection rule installed")

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if packet is None or not packet.parsed:
            return

        source_mac = packet.src.toStr()
        if source_mac in blacklist:
            return

        if packet.type != packet.ARP_TYPE:
            return

        arp = packet.next
        source_ip = arp.protosrc.toStr()
        claimed_mac = arp.hwsrc.toStr()

        if source_ip not in valid_arp:
            valid_arp[source_ip] = claimed_mac
            log.info("ARP learned: %s -> %s", source_ip, claimed_mac)
            return

        expected_mac = valid_arp[source_ip]
        if expected_mac == claimed_mac:
            return

        log.warning(
            "ARP spoofing detected: IP %s announced by %s instead of %s",
            source_ip,
            claimed_mac,
            expected_mac,
        )

        blacklist.add(claimed_mac)

        drop = of.ofp_flow_mod()
        drop.priority = 60000
        drop.match.dl_src = arp.hwsrc
        drop.actions = []
        event.connection.send(drop)

        log.warning("Source %s blocked with a high-priority OpenFlow DROP rule", claimed_mac)


def launch():
    core.registerNew(ARPDefense)
