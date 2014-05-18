#!/bin/bash

echo "Checking dependency..."
apt-get install mosh libio-pty-easy-perl

# Exit on any failure
set -e

# Check for uninitialized variables
set -o nounset

ctrlc() {
	killall -9 python
	mn -c
	exit
}

trap ctrlc SIGINT

start=`date`
exptid=`date +%b%d-%H:%M`

rootdir=mosh-$exptid

echo -e "\nStarting mosh experiment..."

dir=$rootdir
python mosh.py --bw-host 1000 --delay 43.5 --dir $dir
python plot_delay.py $rootdir 

echo "Started at" $start
echo "Ended at" `date`
