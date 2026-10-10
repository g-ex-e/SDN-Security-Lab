#!/usr/bin/env bash
set -euo pipefail

mode="${1:-baseline}"
cd /opt/pox

case "$mode" in
    baseline)
        exec ./pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning
        ;;
    dos)
        exec ./pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning ext.dos_defense
        ;;
    arp)
        exec ./pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning ext.arp_defense
        ;;
    *)
        echo "Usage: run-controller {baseline|dos|arp}" >&2
        exit 1
        ;;
esac
