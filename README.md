## Netpy - The best python3 networking tool in the world.

We can absolutely sure this is the best PYTHON3 TCP/UDP 
NETWORK CONNECTION TOOL in the world. You can try it now.

Netpy is a 'python netcat' with all the networking features. 
Netpy is a custom tcp/udp network tool used for reading or 
writing from TCP and UDP sockets like network debugging, port 
scanning, transferring files, and port listening, ... and it 
also can be used as a backdoor shell (pentesting). It's a good 
investigation tool for administrators, programmers, and pen
testers.

Usage:

**Listen: python3 np.py -lvp [PORT] [-OPTIONS]**

**Connect: python3 np.py -t [ADDRESS] -p [PORT] [-OPTIONS]**

**Scan: python3 np.py -t [ADDRESS] -p [MIN_PORT-MAX_PORT] -z [-OPTIONS]**

****
Example usage:


*python3 np.py -lvp 4444 -e cmd*

*python3 np.py -t 127.0.0.1 -p 4444*

*python3 np.py -lp 5000 -e powershell -u*

*python3 np.py -t 127.0.0.1 -p 1000-8000 -z*

*python3 np.py -t 127.0.0.1 -p 8000-8081 -e /bin/bash -u*

*python3 np.py -l -p 8080 -e myprogram.type*



Created by toidihack(hacking at HackerOne and Bugcrowd)
 
