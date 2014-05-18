import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import scipy.stats as st 
import numpy 
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


# Setting up median points 
medianSSH=len(delaySSH)/2-1
strSSH='median: %.3f ms' % (delaySSH[medianSSH]*1000)
print medianSSH, delaySSH[medianSSH], percentageSSH[medianSSH], strSSH
medianMOSH=len(delayMOSH)/2-1
strMOSH='median: %.3f ms' % (delayMOSH[medianMOSH]*1000)
print medianMOSH, delayMOSH[medianMOSH], percentageMOSH[medianMOSH], strMOSH
medianOffset=(5,-10)

# Setting up mean points 
meanSSH=numpy.mean(delaySSH)
pctMeanSSH=st.percentileofscore(delaySSH, meanSSH, kind='weak')
strMeanSSH='mean: %.3f ms' % (meanSSH*1000)
print meanSSH, pctMeanSSH
meanMOSH=numpy.mean(delayMOSH)
pctMeanMOSH=st.percentileofscore(delayMOSH, meanMOSH, kind='weak')
strMeanMOSH='mean: %.3f ms' % (meanMOSH*1000)
print meanMOSH, pctMeanMOSH
meanOffset=(5,5)

plt.figure()
plt.plot(delaySSH, percentageSSH)
plt.plot(delayMOSH, percentageMOSH)
plt.title('Cumulative distribution of keystroke response\n\
        times with Sprint EV-DO (3G) Internet service')
#Median
plt.plot(delaySSH[medianSSH], percentageSSH[medianSSH], 'ro')
plt.plot(delayMOSH[medianMOSH], percentageMOSH[medianMOSH], 'ro')
plt.annotate(strSSH,(delaySSH[medianSSH], percentageSSH[medianSSH]), 
        xytext=medianOffset, textcoords='offset points')
plt.annotate(strMOSH,(delayMOSH[medianMOSH], percentageMOSH[medianMOSH]), 
        xytext=medianOffset, textcoords='offset points')
#Mean
plt.plot(meanSSH, pctMeanSSH, 'bo')
plt.plot(meanMOSH, pctMeanMOSH, 'bo')
plt.annotate(strMeanSSH,(meanSSH, pctMeanSSH),
        xytext=meanOffset, textcoords='offset points')
plt.annotate(strMeanSSH,(meanMOSH, pctMeanMOSH),
        xytext=meanOffset, textcoords='offset points')
#Output
plt.savefig(curDir+'/graph.png',bbox_inches='tight')
