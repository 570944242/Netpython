#!/usr/bin/python3

import subprocess

cmd = input('Netpython command line: ')
try:
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
except:
    out = 'Invalid command line'
print(out)
