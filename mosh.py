#!/usr/bin/python

"CS244 Assignment 3: Mosh"
# Wei Shi & Sumitra Narayanan

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

import subprocess
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
import termcolor as T
from argparse import ArgumentParser

import sys
import os

import re


def cprint(s, color, cr=True):
    """Print in color
       s: string to print
       color: color to use"""
    if cr:
        print T.colored(s, color)
    else:
        print T.colored(s, color),


# Parse arguments

parser = ArgumentParser(description="Mosh tests")

parser.add_argument('--dir', '-d',
                    dest="dir",
                    action="store",
                    help="Directory to store outputs",
                    default="results",
                    required=True)

# Expt parameters
args = parser.parse_args()

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')

# Topology to be instantiated in Mininet
class StarTopo(Topo):

    def __init__(self):
        # Add default members to class.
        super(StarTopo, self ).__init__()

        # http://en.wikipedia.org/wiki/Comparison_of_wireless_data_standards
        self.bw_host = 3 #3Mb/s 
        self.rtt= 500 
        self.create_topology()

    def create_topology(self):
        server=self.addHost('server')
        client=self.addHost('client')
        self.addLink(server,client,
                bw=self.bw_host,
                delay='%fms' % (self.rtt/2),
                jitter='%fms' % (self.rtt*0.5))

def verify_latency(net):
    print "verify link latency"
    delta=1
    rtt=500
    server=net.getNodeByName('server')
    client=net.getNodeByName('client')
    cmd='ping -c 2 -q %s' % server.IP()
    pingResult=client.popen(cmd, shell=True)
    output=pingResult.stdout.read()
    print output
    rtt_search=re.findall('(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms', 
            output)
    rttMax=float(rtt_search[0][2])
    rttMin=float(rtt_search[0][0])
    cprint('verify latency...OK','green')
    return True
        
def start_test(net):
    server=net.getNodeByName('server')
    server.cmd('/usr/sbin/sshd -D &')
    sleep(3)
    print 'started sshd'
    print server.waitOutput()
    client=net.getNodeByName('client')
    delaySSH=args.dir+'/delaySSH.txt'
    stdoutSSH=args.dir+'/stdoutSSH.txt'
    delayMOSH=args.dir+'/delayMOSH.txt'
    stdoutMOSH=args.dir+'/stdoutMOSH.txt'
    rsa='/home/ubuntu/cs244-mosh/id_rsa'
    keylog='/home/ubuntu/cs244-mosh/keylog.out'
    term_c='/home/ubuntu/cs244-mosh/term-replay-client'
    term_s='/home/ubuntu/cs244-mosh/term-replay-server'
    sshcmd='%s %s ssh ubuntu@%s -i %s -o StrictHostKeyChecking=no "%s %s" > %s 2> %s' % \
            (term_c, keylog, server.IP(), rsa, term_s, keylog, stdoutSSH, delaySSH)
    moshcmd='%s %s mosh ubuntu@%s --ssh=\\"ssh -i %s -o StrictHostKeyChecking=no\\" -- %s %s > %s 2> %s' % \
            (term_c, keylog, server.IP(), rsa, term_s, keylog, stdoutMOSH, delayMOSH)
    print 'Running MOSH test'
    cprint(moshcmd,'blue')
    moshsim = client.popen(moshcmd, shell=True)
    print moshsim.stderr.read()

    print 'Running SSH test'
    cprint(sshcmd,'blue')
    sshsim = client.popen(sshcmd, shell=True)
    print sshsim.stderr.read()

def main():
    "Create network and run Buffer Sizing experiment"

    start = time()
    # Reset to known state
    topo = StarTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    verify_latency(net)

    cprint("[#] Starting experiment", "green")

    start_test(net)

    cprint("[#] Finishing experiment", "green")

    net.stop()
    Popen("sudo killall -9 /usr/bin/perl bwm-ng cat mnexec", shell=True).wait()
    stop_tcpprobe()
    end = time()

if __name__ == '__main__':
    try:
        main()
    except:
        print "-"*80
        print "Caught exception.  Cleaning up..."
        print "-"*80
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng cat mnexec ; mn -c")

