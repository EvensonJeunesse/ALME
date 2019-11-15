#!/bin/bash
sudo echo "starting..."
sudo service network-manager stop
sudo ifconfig wlp5s0 down
sudo iwconfig wlp5s0 mode monitor
sudo ifconfig wlp5s0 up
sudo iwconfig wlp5s0
echo "wlp5s0 in monitor mode"
