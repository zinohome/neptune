#!/bin/bash
FIND_FILE="/opt/neptune/config/settings.ini"
FIND_STR="settings"
if [ `grep -c "$FIND_STR" $FIND_FILE` -ne '0' ];then
    echo "settings exist"
else
    cp /opt/neptune/config/settings_default.ini /opt/neptune/config/settings.ini
fi
FIND_FILE="/opt/neptune/config/gunicorn.py"
FIND_STR="workers"
if [ `grep -c "$FIND_STR" $FIND_FILE` -ne '0' ];then
    echo "gunicorn config exist"
else
    cp /opt/neptune/config/gunicorn_default.py /opt/neptune/config/gunicorn.py
fi
cd /opt/neptune && \
nohup /opt/neptune/venv/bin/gunicorn -c /opt/neptune/config/gunicorn.py main:app >> /tmp/neptune.log 2>&1 &