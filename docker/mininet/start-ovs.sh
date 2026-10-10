#!/usr/bin/env bash
set -euo pipefail

mkdir -p /var/run/openvswitch /etc/openvswitch
rm -f /var/run/openvswitch/db.sock /var/run/openvswitch/*.pid

if [ ! -f /etc/openvswitch/conf.db ]; then
    ovsdb-tool create /etc/openvswitch/conf.db /usr/share/openvswitch/vswitch.ovsschema
fi

ovsdb-server \
    --remote=punix:/var/run/openvswitch/db.sock \
    --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
    --pidfile \
    --detach

ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach

printf '%s\n' 'Open vSwitch is ready.'
exec tail -f /dev/null
