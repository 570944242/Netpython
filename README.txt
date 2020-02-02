                 ____
            ^  ^   _ \
  ___      \' '/  \ _ \       _             ___
 |</>|---(((\_/)))-\ _ \-----|_|-----------|</>|
 |___|             / _ /                   |___|
                  / _ /                    
                 / _ /
                / _ /

Netpython 1.10
==============

This Netpython for python environment is a advanced networking utility for reading 
from and writing to network connections using TCP/UDP protocol written in python that 
will help all developers who are working in the python environment. It designed for any 
network purposes, can be a "back-end"tool that can run programs and scripts remotely, 
easily upon the connection. This netpython is an idea from netcat which is a feature-rich 
network debugging and exploration tool and have inspired the author of this tool. The 
author belive that this tool can be a alternative solution for minimize cyber attacks 
(replace netcat with netpython can stop hackers to do a reverse or bind shell, except 
hackers known that the server is using netpython as netcat) and for who are working with 
python or who are using Windows which doesn't have netcat as the default. Speacial, 
netpython has been tested with VirusTotal and returned the true negative result. That mean 
this tool will never been detected by any anti-virus programs. 


Netpython has a very simple usage, "np.py -lvp port" or "np.py -t host -p port" can 
creates a TCP connection (also support the UDP connection) to the given port and the 
given host. More options are shown in the netpython help message "np.py -h". If you are
using python2, use "np2.py". I am working on "np2" to it can I and O at the same time.


Some the netpython features:

 - Port scanning
 - Transferring files
 - Port listening
 - Connecting to the server
 - Create a shell upon connections
 - Server chatting
 - Network debugging
Netpython can also used as a backdoor.


The origin of Netpython
=======================
 ---Bulding---
When author known about Netcat, he was so exciting with it, with a lot of network features. 
But unfortunately, Windows doesn't have Netcat. He was so sad but at that time, he just finished
the python course to be a good python developer so he made this. Although after a time, he known
that there is a netcat for Windows, he still continue with his tool because the Anti-virus has
blocked his netcat. And now here it is!

 ---Time---
Finished in 2019

 ---Code---
Using the python socket, subprocess modules. (And some other important python modules: os, sys, 
...). Author has tried to don't use any "required download" modules.

 ---License---
Although the author still haven't registered any license yet but please don't copy this in any
way. 

 ---Name---
- Netcat ==> The cat of networking (C, '.c' -> Cat)
- Netpython ==> The python of networking (Python, '.py' -> Python)
