#!/bin/bash
sudo echo "starting..."
sudo ifconfig wlp5s0 down
sudo iwconfig wlp5s0 mode managed
sudo ifconfig wlp5s0 up
sudo service network-manager start
sudo iwconfig wlp5s0
echo "wlp5s0 in managed mode"
