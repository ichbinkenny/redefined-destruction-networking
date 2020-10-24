#!/bin/sh
# This script replaces the old wpa_supplicant file with the new connection's info

ssid=$1
psk=$2

sudo printf "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=US\n\nnetwork={\n\tssid=$ssid\n\tpsk=$2\n}\n" > /etc/wpa_supplicant.conf
