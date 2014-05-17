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

#python $plotpath/plot_queue.py -f $dir/qlen_$iface.txt -o $dir/q.png
#python $plotpath/plot_tcpprobe.py -f $dir/tcp_probe.txt -o $dir/cwnd.png --histogram


#python plot-results.py --dir $rootdir -o $rootdir/result.png
echo "Started at" $start
echo "Ended at" `date`
