Installation
==============

    sudo apt-get install mosh libio-pty-easy-perl

Recording key log
==============

    ./term-save ./keylog.out

Running stm-data scripts
==============

SSH

    ./term-replay-client ./keylog.out ssh ubuntu@server.IP() "./term-replay-server ./keylog.out"

Mosh

    ./term-replay-client ./keylog.out mosh ubuntu@server.IP() "./term-replay-server ./keylog.out"
