cs244-mosh
==========

Reproducing Mosh research paper:
http://mosh.mit.edu/mosh-paper.pdf

+ Monday, May 19 2014, 5pm: Intermediate project report
+ Monday, June 2 2014, 11:59pm: Final report
+ Saturday, June 7 2014, 5 pm: Validation

Installation
==============

### Setting up instance

We use the CS244-Spr14-Mininet image as a starting point.
Basically you need to do these steps:

+ Create a community instance image: `ami-e2b6ded2` 
+ Choose m3.medium for Instance Type
+ Open port 22 for SSH
+ **IMPORTANT** Open all UDP ports by adding the rule `All UDP` with source `Anywhere`
+ Pick your SSH key pair
+ Launch & login

If you are unclear, 
follow the [guide](http://www.stanford.edu/class/cs244/ec2.html),
and remember to open all UDP ports.

### Running the experiment

Get source code and run the script. 
```
git clone https://github.com/weishi/cs244-mosh.git
cd cs244-mosh
sudo ./run.sh
```
The script will first try to install any dependency packages.
The script will run 3 sets of experiment.
The first one will reproduce the result from paper.
The other two are for sensitivity analysis.
The second one will run the simulation over a WiFi link with 10% loss rate.
The thrid one will run the simulation over a 4G LTE link.

This first replay(SSH/MOSH) may take up to 15min, because it uses a large dataset.
The other two may take up to 5min. They use a smaller dataset, because the
loss rate will significantly increase the simulation time.

Sometimes(very rarely), the second replay(sensitivity analysis 1) may get stuck
due to the randomness of loss. 
The problem usually goes away after restarting the script.
To see the progress, you can monitor stdoutSSH.txt/stdoutMOSH.txt, etc.

### Result
The result graphs are created in 'mosh-{timestamp}' directory.

+ `graph.png`: the main result that should match Figure 2 in the paper. 
+ `graph_sen1.png`: the result for sensitivity analysis 1.
+ `graph_sen2.png`: the result for sensitivity analysis 2.
