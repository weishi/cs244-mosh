#!/bin/bash

if [ -f id_rsa.pub ];
then
	echo "Checking dependency..."
	apt-get -y install python-software-properties libio-pty-easy-perl
	sudo add-apt-repository -y ppa:keithw/mosh
	sudo apt-get update
	sudo apt-get -y install mosh
	echo -e "Done."

	echo -e "\nImporting public key..."
	cat id_rsa.pub >> /home/ubuntu/.ssh/authorized_keys
	mv id_rsa.pub id_rsa.done
	echo -e "Done."
fi

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

python mosh.py --dir $rootdir
python plot_delay.py $rootdir delaySSH.txt delayMOSH.txt graph.png 'Sprint 3G'
python plot_delay.py $rootdir delaySSH_sen1.txt delayMOSH_sen1.txt graph_sen1.png 'Sprint 3G + 30%loss'
python plot_delay.py $rootdir delaySSH_sen2.txt delayMOSH_sen2.txt graph_sen2.png '4G LTE'

echo "Started at" $start
echo "Ended at" `date`
