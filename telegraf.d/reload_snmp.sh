#!/bin/bash

sudo rm /etc/telegraf/telegraf.d/*.conf
cd /opt/lnetd/telegraf.d/
sudo python3 generate_telegraf_config_all.py

sudo service telegraf reload > /dev/null
