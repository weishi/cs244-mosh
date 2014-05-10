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
from util.monitor import monitor_qlen
from util.helper import stdev

import re


# Number of samples to skip for reference util calibration.
CALIBRATION_SKIP = 10

# Number of samples to grab for reference util calibration.
CALIBRATION_SAMPLES = 10

# Time to wait between samples, in seconds, as a float.
SAMPLE_PERIOD_SEC = 0.8

# Time to wait for first sample, in seconds, as a float.
SAMPLE_WAIT_SEC = 3.0


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
parser.add_argument('--bw-host', '-B',
                    dest="bw_host",
                    type=float,
                    action="store",
                    help="Bandwidth of host links",
                    required=True)

parser.add_argument('--delay',
                    dest="delay",
                    type=float,
                    help="Delay in milliseconds of host links",
                    default=87)

parser.add_argument('--dir', '-d',
                    dest="dir",
                    action="store",
                    help="Directory to store outputs",
                    default="results",
                    required=True)

parser.add_argument('--target',
                    dest="target",
                    help="Target utilisation",
                    type=float,
                    default=TARGET_UTIL_FRACTION)

# Expt parameters
args = parser.parse_args()

CUSTOM_IPERF_PATH = args.iperf
assert(os.path.exists(CUSTOM_IPERF_PATH))

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')

# Topology to be instantiated in Mininet
class StarTopo(Topo):
    "Star topology for Buffer Sizing experiment"

    def __init__(self, bw_host=None, delay=None):
        # Add default members to class.
        super(StarTopo, self ).__init__()

        # http://en.wikipedia.org/wiki/Comparison_of_wireless_data_standards
        self.bw_host = 3 #3Mb/s 
        self.rtt= 500 
        self.create_topology()

    def create_topology(self):
        server=self.addHost('server')
        client=self.addHost('client')
        self.addLink(server,client,bw=self.bw_host,delay='%fms' % (args.rtt/2))

def start_tcpprobe():
    "Install tcp_probe module and dump to file"
    os.system("rmmod tcp_probe 2>/dev/null; modprobe tcp_probe;")
    Popen("cat /proc/net/tcpprobe > %s/tcp_probe.txt" %
          args.dir, shell=True)

def stop_tcpprobe():
    os.system("killall -9 cat; rmmod tcp_probe &>/dev/null;")

def count_connections():
    "Count current connections in iperf output file"
    out = args.dir + "/iperf_server.txt"
    lines = Popen("grep connected %s | wc -l" % out,
                  shell=True, stdout=PIPE).communicate()[0]
    return int(lines)

def set_speed(iface, spd):
    "Change htb maximum rate for interface"
    cmd = ("tc class change dev %s parent 5:0 classid 5:1 "
           "htb rate %s burst 15k" % (iface, spd))
    os.system(cmd)

def get_txbytes(iface):
    f = open('/proc/net/dev', 'r')
    lines = f.readlines()
    for line in lines:
        if iface in line:
            break
    f.close()
    if not line:
        raise Exception("could not find iface %s in /proc/net/dev:%s" %
                        (iface, lines))
    # Extract TX bytes from:
    #Inter-|   Receive                                                |  Transmit
    # face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    # lo: 6175728   53444    0    0    0     0          0         0  6175728   53444    0    0    0     0       0          0
    return float(line.split()[9])

def get_rates(iface, nsamples=NSAMPLES, period=SAMPLE_PERIOD_SEC,
              wait=SAMPLE_WAIT_SEC):
    """Returns the interface @iface's current utilization in Mb/s.  It
    returns @nsamples samples, and each sample is the average
    utilization measured over @period time.  Before measuring it waits
    for @wait seconds to 'warm up'."""
    # Returning nsamples requires one extra to start the timer.
    nsamples += 1
    last_time = 0
    last_txbytes = 0
    ret = []
    sleep(wait)
    while nsamples:
        nsamples -= 1
        txbytes = get_txbytes(iface)
        now = time()
        elapsed = now - last_time
        #if last_time:
        #    print "elapsed: %0.4f" % (now - last_time)
        last_time = now
        # Get rate in Mbps; correct for elapsed time.
        rate = (txbytes - last_txbytes) * 8.0 / 1e6 / elapsed
        if last_txbytes != 0:
            # Wait for 1 second sample
            ret.append(rate)
        last_txbytes = txbytes
        print '.',
        sys.stdout.flush()
        sleep(period)
    return ret

def avg(s):
    "Compute average of list or string of values"
    if ',' in s:
        lst = [float(f) for f in s.split(',')]
    elif type(s) == str:
        lst = [float(s)]
    elif type(s) == list:
        lst = s
    return sum(lst)/len(lst)

def median(l):
    "Compute median from an unsorted list of values"
    s = sorted(l)
    if len(s) % 2 == 1:
        return s[(len(l) + 1) / 2 - 1]
    else:
        lower = s[len(l) / 2 - 1]
        upper = s[len(l) / 2]
        return float(lower + upper) / 2

def format_floats(lst):
    "Format list of floats to three decimal places"
    return ', '.join(['%.3f' % f for f in lst])

def ok(fraction):
    "Fraction is OK if it is >= args.target"
    return fraction >= args.target

def format_fraction(fraction):
    "Format and colorize fraction"
    if ok(fraction):
        return T.colored('%.3f' % fraction, 'green')
    return T.colored('%.3f' % fraction, 'red', attrs=["bold"])

def verify_latency(net):
    print "verify link latency"
    delta=1
    server=net.getNodeByName('h3')
    for h in ['h1', 'h2']:
        hptr=net.getNodeByName(h)
        cmd='ping -c 5 -q %s' % server.IP()
        pingResult=hptr.popen(cmd, shell=True)
        output=pingResult.stdout.read()
        rtt_search=re.findall('(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms', 
                output)
        rttMax=float(rtt_search[0][2])
        rttMin=float(rtt_search[0][0])
        if(rttMin < args.delay*2-delta or rttMax > args.delay*2+delta):
            return False 
    cprint('verify latency...OK','green')
    return True
        
# TODO: Fill in the following function to
# Start iperf on the receiver node
# Hint: use getNodeByName to get a handle on the sender node
# Hint: iperf command to start the receiver:
#       '%s -s -p %s > %s/iperf_server.txt' %
#        (CUSTOM_IPERF_PATH, 5001, args.dir)
# Note: The output file should be <args.dir>/iperf_server.txt
#       It will be used later in count_connections()

def start_receiver(net):
    print 'starting receiver iperf'
    h3=net.getNodeByName('h3')
    cmd='%s -s -p %s > %s/iperf_server.txt' % (CUSTOM_IPERF_PATH, 5001, args.dir)
    h3.popen(cmd, shell=True)

# TODO: Fill in the following function to
# Start args.nflows flows across the senders in a round-robin fashion
# Hint: use getNodeByName to get a handle on the sender (A or B in the
# figure) and receiver node (C in the figure).
# Hint: iperf command to start flow:
#       '%s -c %s -p %s -t %d -i 1 -yc -Z %s > %s/%s' % (
#           CUSTOM_IPERF_PATH, server.IP(), 5001, seconds, args.cong, args.dir, output_file)
# It is a good practice to store output files in a place specific to the
# experiment, where you can easily access, e.g., under args.dir.
# It will be very handy when debugging.  You are not required to
# submit these in your final submission.

def start_senders(net):
    # Seconds to run iperf; keep this very high
    seconds = 3600
    server=net.getNodeByName('h3')
    for h in ['h1', 'h2']:
        hptr=net.getNodeByName(h)
        output_file='iperf_'+h+'.txt'
        cmd='%s -c %s -p %s -t %d -i 1 -yc -Z %s > %s/%s' % \
            (CUSTOM_IPERF_PATH, server.IP(), 5001, 
             seconds, args.cong, args.dir, output_file)
        for flow in range(args.nflows):
            hptr.popen(cmd, shell=True)

def main():
    "Create network and run Buffer Sizing experiment"

    start = time()
    # Reset to known state
    topo = StarTopo(n=args.n, bw_host=args.bw_host,
                    delay='%sms' % args.delay,
                    bw_net=args.bw_net, maxq=args.maxq)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    # TODO: verify latency and bandwidth of links in the topology you
    # just created.
    verify_latency(net)

    start_receiver(net)

    start_tcpprobe()

    cprint("Starting experiment", "green")

    start_senders(net)

    # Store output.  It will be parsed by run.sh after the entire
    # sweep is completed.  Do not change this filename!
    output = "%d %s %.3f\n" % (total_flows, ret, ret * 1500.0)
    open("%s/result.txt" % args.dir, "w").write(output)

    # Shut down iperf processes
    os.system('killall -9 ' + CUSTOM_IPERF_PATH)

    net.stop()
    Popen("killall -9 top bwm-ng tcpdump cat mnexec", shell=True).wait()
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
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf; mn -c")

