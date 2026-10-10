FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    dsniff \
    hping3 \
    iproute2 \
    iputils-ping \
    mininet \
    net-tools \
    openvswitch-common \
    openvswitch-switch \
    procps \
    python3 \
    tcpdump \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/lab

COPY topology/topology.py /opt/lab/topology.py
COPY docker/mininet/start-ovs.sh /usr/local/bin/start-ovs

RUN chmod +x /usr/local/bin/start-ovs

CMD ["/usr/local/bin/start-ovs"]
