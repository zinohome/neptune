#!/bin/bash
set -e
set -x
apt-get update && DEBIAN_FRONTEND=noninteractive && \
apt -y dist-upgrade && \
apt-get install -y --no-install-recommends net-tools libsasl2-dev curl wget procps netcat git libnss3-tools pip && \
pip install virtualenv && \
cd /opt && \
git clone https://github.com/zinohome/neptune.git && \
cd /opt/neptune && \
git pull && \
chmod 755 mkcert-v1.4.3-linux-amd64 && mv mkcert-v1.4.3-linux-amd64 mkcert && mv mkcert /usr/bin/ && \
mkcert -install && \
mkdir -p /opt/neptune/log && \
mkdir -p /opt/neptune/cert && \
mkcert -cert-file /opt/neptune/cert/cert.pem -key-file /opt/neptune/cert/cert-key.pem zinohome.com neptune.zinohome.com localhost 127.0.0.1 ::1 && \
virtualenv venv && \
. venv/bin/activate && \
pip install -r requirements.txt && \
cd /opt/neptune && \
cp /bd_build/50_start_neptune.sh  /etc/my_init.d/ && \
chmod 755 /etc/my_init.d/50_start_neptune.sh



