#!/bin/sh

sudo ifdown 'wlan0'
sleep 5
sudo ifup --force 'wlan0'
ping -c4 192.168.72.1 > /dev/null

if [$? == 0]
then
    echo "SUCCESS!"
else
    echo "FAILURE! NETWORK CONN NOT ESTABLISHED!"
fi