## Py-shell - The best python3 backdoor shell in the world.

We can absolutely sure this is the best PYTHON3 SHELL in the 
world until now. You can try it now.

Python netcat for reverse or bind shell. Py-shell is a custom 
network tool to create backdoor shell (pentesting) and some 
other network purpose like connection testing or remote command 
excution (for who want to help others remotely).

Usage:

**Listen: python3 pyshell.py -lvp [PORT] [-OPTIONS]**

**Connect: python3 pyshell.py -t [ADDRESS] -p [PORT] [-OPTIONS]**

**Scan: python3 pyshell.py -t [ADDRESS] -p [MIN_PORT-MAX_PORT] -z [-OPTIONS]**

****
Example usage:


*python3 pyshell.py -lvp 4444 -e cmd*

*python3 pyshell.py -t 127.0.0.1 -p 4444*

*python3 pyshell.py -lp 5000 -e powershell*

*python3 pyshell.py -t 127.0.0.1 -p 1000-8000 -z*

*python3 pyshell.py -t 127.0.0.1 -p 8000-8081 -e /bin/bash*

*python3 pyshell.py -l -p 8080 -e myprogram.end*



Created by toidihack(hacking at HackerOne and Bugcrowd)
 
