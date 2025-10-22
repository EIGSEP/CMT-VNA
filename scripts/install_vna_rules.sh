#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root." 
   exit 1
fi

cat <<EOF > /etc/udev/rules.d/usb-cmt-vna.rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="2226", MODE="0666"
SUBSYSTEM=="usb_device", ATTRS{idVendor}=="2226", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="36bf", MODE="0666"
SUBSYSTEM=="usb_device", ATTRS{idVendor}=="36bf", MODE="0666"
EOF

udevadm control --reload-rules
udevadm trigger
systemctl daemon-reload
service udev reload
service udev restart

echo "Rules successfully added and loaded."
echo "Please, reconnect VNA Devices for apply rules"
