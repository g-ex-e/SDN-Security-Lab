FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone --depth 1 https://github.com/noxrepo/pox.git

WORKDIR /opt/pox

COPY controllers/arp_defense.py /opt/pox/ext/arp_defense.py
COPY controllers/dos_defense.py /opt/pox/ext/dos_defense.py
COPY docker/pox/run-controller.sh /usr/local/bin/run-controller

RUN chmod +x /usr/local/bin/run-controller

EXPOSE 6633/tcp

CMD ["tail", "-f", "/dev/null"]
