Installation
==============

    sudo apt-get install mosh libio-pty-easy-perl

Download scripts
==============

    git clone https://github.com/keithw/stm-data.git

Recording key log
==============

    ./term-save ./keylog.out

Use case:
+ cd into different directories
+ editing a file with vim/emacs, etc
+ networking
+ check man page
+ ...?

Running stm-data scripts
==============

SSH via Mininet

    ./term-replay-client ./keylog.out ssh ubuntu@server.IP() "./term-replay-server ./keylog.out"

Mosh via Mininet

    ./term-replay-client ./keylog.out mosh ubuntu@server.IP() "./term-replay-server ./keylog.out"

Testing on command line interactively

    git clone https://github.com/weishi/cs244-mosh.git
    copy private key to /home/ubuntu/.ssh/id_rsa
    ./term-replay-client ./keylog.out ssh ubuntu@localhost "/home/ubuntu/cs244-mosh/term-replay-server /home/ubuntu/cs244-mosh/keylog.out" 2> test
