#!/bin/bash
sudo echo "starting..."
sudo ifconfig $1 down
sudo iwconfig $1 mode managed
sudo ifconfig $1 up
sudo service network-manager start
sudo iwconfig $1
echo $1" in managed mode"
