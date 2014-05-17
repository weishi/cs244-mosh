import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import scipy.stats as st 
import sys

curDir=sys.argv[1]
delaySSHfile = curDir+'/delaySSH.txt'
delayMOSHfile = curDir+'/delayMOSH.txt'
delaySSH= []
delayMOSH= []
percentageSSH = []
percentageMOSH = []

for line in open(delaySSHfile, 'r'):
    if 'Delay' in line:
        line=line.strip().split()
        delay=float(line[1])
        delaySSH.append(delay)

delaySSH.sort()
delaySSH=delaySSH[0:-1]
for val in delaySSH:
    percentageSSH.append(st.percentileofscore(delaySSH, val, kind='weak'))

for line in open(delayMOSHfile, 'r'):
    if 'Delay' in line:
        line=line.strip().split()
        delay=float(line[1])
        delayMOSH.append(delay)

delayMOSH.sort()
delayMOSH=delayMOSH[0:-1]
for val in delayMOSH:
    percentageMOSH.append(st.percentileofscore(delayMOSH, val, kind='weak'))

plt.figure()
plt.plot(delaySSH, percentageSSH)
plt.plot(delayMOSH, percentageMOSH)
plt.title('CDF')
plt.savefig('graph.png',bbox_inches='tight')
