from collections import defaultdict
import time

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4

log = core.getLogger()

THRESHOLD = 50
WINDOW_SECONDS = 1.0

counters = defaultdict(lambda: {"count": 0, "started_at": time.time()})
blacklist = set()


class DoSDefense(object):
    def __init__(self):
        core.openflow.addListeners(self)
        log.info("DoS defense module loaded")

    def _handle_ConnectionUp(self, event):
        log.info("Switch connected: %s", event.connection)

        flow = of.ofp_flow_mod()
        flow.priority = 50000
        flow.match.dl_type = ethernet.IP_TYPE
        flow.match.nw_proto = ipv4.TCP_PROTOCOL
        flow.match.tp_dst = 80
        flow.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
        event.connection.send(flow)

        log.info("HTTP/TCP traffic inspection rule installed")

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if packet is None or not packet.parsed:
            return

        source_mac = str(packet.src)
        if source_mac in blacklist:
            return

        tcp = packet.find("tcp")
        if tcp is None or not tcp.SYN:
            return

        now = time.time()
        counter = counters[source_mac]

        if now - counter["started_at"] >= WINDOW_SECONDS:
            counter["count"] = 0
            counter["started_at"] = now

        counter["count"] += 1

        if counter["count"] <= THRESHOLD:
            return

        log.warning(
            "SYN flood detected from %s (%d SYN in current window)",
            source_mac,
            counter["count"],
        )

        blacklist.add(source_mac)

        drop = of.ofp_flow_mod()
        drop.priority = 60000
        drop.match.dl_src = packet.src
        drop.actions = []
        event.connection.send(drop)

        log.warning("Source %s blocked with a high-priority OpenFlow DROP rule", source_mac)


def launch():
    core.registerNew(DoSDefense)
