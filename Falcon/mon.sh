#!/bin/bash
sudo echo "starting..."
sudo service network-manager stop
sudo ifconfig $1 down
sudo iwconfig $1 mode monitor
sudo ifconfig $1 up
sudo iwconfig $1
sudo service network-manager start
echo $1" in monitor mode"
