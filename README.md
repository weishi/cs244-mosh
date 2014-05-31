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

+ Create a community instance image: ami-e2b6ded2 
+ Choose m3.medium for Instance Type
+ Open port 22 for SSH
+ **IMPORTANT** Open all UDP ports by adding the rule 'All UDP' with source 'Anywhere' 
+ Pick your SSH key pair
+ Launch & login

If you are unclear, 
follow the [guide](http://www.stanford.edu/class/cs244/ec2.html),
and remember to open all UDP ports 

### Running the experiment

+ Get source code

    git clone https://github.com/weishi/cs244-mosh.git

+ Run the script. 

    cd cs244-mosh
    sudo ./run.sh

The script will first try to install any dependency packages.
Each replay(SSH/MOSH) may take up to 15min.
To see the progress, you can monitor stdoutSSH.txt/stdoutMOSH.txt.

+ The result graph.png is created in 'mosh-{timestamp}' directory
