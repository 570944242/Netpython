#!/usr/bin/python3

import sys
import socket
import getopt
import threading
import subprocess
import os
from random import randrange

listen = False
execute = ''
target = ""
port = None
zero = False
ver = False
typ = socket.SOCK_STREAM
rand = False
timeout = None
pwd = None
clrf = False
name = None
alive = False
mver = False

if sys.platform == 'win32':
    e = b'\n'
else:
    e = b''


banner = r'''
                 ____
            ^  ^   _ \
  ___      \' '/  \ _ \       _             ___
 |</>|---(((\_/)))-\ _ \-----|_|-----------|</>|
 |___|             / _ /                   |___|
                  / _ /                    
                 / _ /
                / _ /
'''

def usage():

    print("""[Netpython github.com/hackerSMinh/Netpython]
Connect: np.py -t hostname -p port[s] [-options]
Listen: np.py -l -p port [-options]
Scan: np.py -t hostname -p min_port-max_port -z [-options]

Options:""")

    print("       -h                     This help")
    print("       -l                     Listen for inbound connects")
    print("       -p port[s]             Port for the connection")
    print("       -e file                Execute program upon connection")
    print("       -c                     Use `-e` as '/bin/bash' in unix and 'cmd' in windows")
    print("       -t addr                Host for the ibound connection")
    print("       -z                     Zero I/O mode (used in port scaning)")
    print("       -v                     Verbose mode")
    print("       -V                     More verbose")
    print("       -u                     UDP protocol mode")
    print("       -r                     Random local or remote ports")
    print("       -w secs                Set timeout for the connection")
    print("       -d pass                Require password to connects")
    print("       -C                     CLRF as line ending (use it when chating)")
    print("       -n name                Send your name as first line (for recognize when chating)")
    print("       -k                     Keep socket alive")
    print("       -b                     Display the Netpython banner")
    print("Port numbers can be individual or ranges: min-max")

    sys.exit(0)


def o(s):
    while 1:
        try:
            data = s.recv(4096).decode()
            print(data, end='')
        except:
            s.close()
            break


def exec_command(command, exe):
    command = command.rstrip()

    try:
        if exe == 'cmd' or 'cmd.exe' in exe or exe == '/bin/bash' or exe == '/bin/sh':
            out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)+e
        else:
            out = subprocess.check_output([exe, command], stderr=subprocess.STDOUT, shell=True)+e

    except subprocess.CalledProcessError:
        if 'powershell' in exe:
            out = b"""%s : The term '%s' is not recognized as the name of a cmdlet, function, script file, or operable program. Check
the spelling of the name, or if a path was included, verify that the path is correct and try again.
At line:1 char:1
+ %s
+ ~~~~~~~
    + CategoryInfo          : ObjectNotFound: (%s:String) [], CommandNotFoundException
    + FullyQualifiedErrorId : CommandNotFoundException

""" % (command.encode(), command.encode(), command.encode(), command.encode())
        elif 'cmd' in exe:
            out = b"'%s' is not recognized as an internal or external command,\noperable program or batch file.\n\n" % command.encode()
        elif exe == '/bin/bash' or exe == '/bin/sh':
            out = b"-bash: %s: command not found\n" % command.encode()
        else:
            out = b''

    return out


def client_handler(client_socket, execute, pwd):
    if pwd != None:
        while 1:
            client_socket.send(b'Enter the password: ')
            pw = client_socket.recv(1024).decode().replace('\n', '')
            if pw == pwd:
                break
            
    if len(execute):
        if sys.platform == 'win32':
            if 'powershell' in execute:
                version = b'\nWindows PowerShell\nCopyright (C) Microsoft Corporation. All rights reserved.\n\n'
                client_socket.send(version + b'PS ' + os.getcwd().encode() + b'>')
            elif 'cmd' in execute:
                version = subprocess.check_output('ver', stderr=subprocess.STDOUT, shell=True) + b'(c) Microsoft Corporation. All rights reserved.\n\n'
                client_socket.send(version + os.getcwd().encode() + b'>')
            else:
                client_socket.send(b'\n')
        elif execute == '/bin/bash' or execute == '/bin/sh':
            usr = subprocess.check_output('whoami', stderr=subprocess.STDOUT, shell=True).decode().replace('\n', '')
            if usr == 'root':
                end = '#'
            else:
                end = '$'
            client_socket.send(('\n%s@%s:%s%s ' % (usr, socket.gethostname(), os.getcwd(), end)).encode())
        else:
            client_socket.send(b'\n')

        while 1:
            try:
                cmd_buffer = client_socket.recv(1024)

                _str = cmd_buffer.decode()
                if not len(_str):
                    out = b'\n'

                if 'cmd' in execute or 'powershell' in execute or execute == '/bin/bash' or execute == '/bin/sh':
                    if _str.replace(' ', '') == 'exit':  
                        client_socket.close()
                        break

                    if not len(_str.replace(' ', '')):
                        out = b''

                    else:
                        if _str.replace(' ', '') == 'cd..':
                            oloc = ''
                            if sys.platform == 'win32':
                                aloc = os.getcwd().split('\\')
                            else:
                                aloc = os.getcwd().split('/')
                            i = 0
                            while i < len(aloc)-1:
                                oloc += aloc[i]+'/'
                                i += 1
                            os.chdir(oloc)
                            out = e

                        elif _str.replace(' ', '') == 'cd' and sys.platform != 'win32':
                            oloc = ''
                            aloc = os.getcwd().split('/')
                            i = 0
                            while i < 3:
                                oloc += aloc[i]+'/'
                                i += 1
                            os.chdir(oloc)
                            out = b''

                        elif _str.replace(' ', '') == 'cd~' and sys.platform != 'win32':
                            usr = subprocess.check_output('whoami', stderr=subprocess.STDOUT, shell=True).decode().replace('\n', '')
                            os.chdir('/home/' + usr)
                            out = b''

                        elif _str.replace(' ', '')[:2] == 'cd' and len(_str.replace(' ', '')) != 2:
                            try:
                                os.chdir(_str.replace('cd', '').replace(' ', ''))
                                out = e
                            except:
                                if 'cmd' in execute:
                                    out = b'The system cannot find the path specified.\n\n'
                                elif 'powershell' in execute:
                                    out = b"""cd : Cannot find path '%s' because it does not exist.
At line:1 char:1
+ cd %s
+ ~~~~~~~
    + CategoryInfo          : ObjectNotFound: (%s:String) [Set-Location], ItemNotFoundException
    + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.SetLocationCommand

""" % (os.getcwd().encode()+b'\\'+_str.replace(' ', '').replace('cd', '').encode(), _str.replace(' ', '').replace('cd', '').encode(), os.getcwd().encode()+b'\\'+_str.replace(' ', '').replace('cd', '').encode())
                                else:
                                    out = b"-bash: cd: %s: No such file or directory\n" % _str.replace(' ', '').replace('cd', '').encode()

                        else:
                            out = exec_command(_str, execute)

                    if sys.platform == 'win32':
                        if 'powershell' in execute:
                            client_socket.sendall(out + b'PS ' + os.getcwd().encode() + b'>')
                        else:
                            client_socket.sendall(out + os.getcwd().encode() + b'>')

                    else:
                        usr = subprocess.check_output('whoami', stderr=subprocess.STDOUT, shell=True).decode().replace('\n', '')
                        if usr == 'root':
                            end = '#'
                        else:
                            end = '$'
                        client_socket.sendall(out + ('%s@%s:%s%s ' % (usr, socket.gethostname(), os.getcwd(), end)).encode())

                else:
                    out = exec_command(_str, execute)
                    client_socket.send(out + b'\n')

            except:
                client_socket.close()
                break


    else:
        if name != None:
            client_socket.send(b'[%s]\n' % name)
        _thread = threading.Thread(target=o, args=[client_socket])
        _thread.start()
        while 1:
            try:
                buffer = input('')
                if port in (80, 443):
                    buffer += '\n' + input()
                if not len(buffer):
                    buffer = '\n'
                if clrf == True:
                    buffer += '\n'
                client_socket.send(buffer.encode())

            except:
                client_socket.close()
                break

    quit()


def client_send(target, port, exe):
    try:
        client = socket.socket(socket.AF_INET, typ)
        if timeout != None:
            client.settimeout(int(timeout))
            
        client.connect((target, port))
        if ver == True:
            print('(UNKNOWN) [%s] %s : Open' % (target, port))
        if alive == True:
            client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if zero == True:
            client.close()

        else:
            try:
                client_thread = threading.Thread(target=client_handler, args=(client, exe, pwd))
                client_thread.start()
            except KeyboardInterrupt:
                print('^C')
                quit()

    except:
        if mver == True:
            print('(UNKNOWN) [%s] %s : Connection failed' % (target, port))

def server_loop(port, exe):
    target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, typ)
    try:
        server.bind((target, port))
    except:
        print("Can't bind at [0.0.0.0] %s" % port)
        quit()

    if ver == True:
        print('Listening on %s ...' % port)

    server.listen(5)
    if timeout != None:
            client.settimeout(int(timeout))

    try:
        client_socket, addr = server.accept()
        if alive == True:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        print('(UNKNOWN) [%s] %s : Connection successfully' % (addr[0], addr[1]))

        try:
            client_thread = threading.Thread(target=client_handler, args=(client_socket, exe, pwd))
            client_thread.start()

        except KeyboardInterrupt:
            print('^C')
            quit()

    except:
        pass


def main():
    global listen
    global port
    global execute
    global target
    global zero
    global ver
    global rand
    global timeout
    global pwd
    global clrf
    global name
    global alive
    global mver

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:zvurw:d:cCn:kVb", ["help", "listen", "execute",
                                                        "target", "port", "zero", "verbose", "udp",
                                                        "random", "timeout", "passwd", "terminal",
                                                        "clrf", "name", "keepalive", "Mverbose", "banner"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h"):
            usage()
        elif o in ("-l"):
            listen = True
        elif o in ("-e", "e"):
            execute = a
        elif o in ("-t"):
            target = a
        elif o in ("-p", "p"):
            port = a
        elif o in ("-z", "z"):
            zero = True
        elif o in ("-v", "v"):
            ver = True
        elif o in ("-u", "u"):
            typ = socket.SOCK_DGRAM
        elif o in ("-r", "r"):
            rand = True
        elif o in ("-w", "w"):
            timeout = a
        elif o in ("-d", "d"):
            pwd = a
        elif o in ("-c", "c"):
            if sys.platform == 'win32':
                execute = 'cmd'
            else:
                execute = '/bin/sh'
        elif o in ("-C", "C"):
            clrf = True
        elif o in ("-n", "n"):
            name = a
        elif o in ("-k", "k"):
            alive = True
        elif o in ("-V", "V"):
            mver = True
        elif o in ("-b", "b"):
            print(banner)
            quit()
        else:
            pass

    if rand:
        while 1:
            port = randrange(1, 65535)
            try:
                s = socket.socket(socket.AF_INET, typ)
                s.bind(('0.0.0.0', port))
                break
            except:
                pass

    if port == None:
        print("Invalid usage: No port[s] (use `-r` to randomize ports)")
        quit()

    if not port.isdigit() or not 65536 > int(port) > 0:
        print('Invalid usage: Invalid port %s' % port)
        quit()

    if timeout != None and not timeout.isdigit():
        print('Invalid usage: Invalid timeout %s' % port)
        quit()

    if not listen and len(target) and '-' in port:
        fport = int(port.split('-')[0])
        lport = int(port.split('-')[1])
        for p in range(fport, lport+1):
            _thread = threading.Thread(target=client_send, args=(target, p, execute))
            _thread.start()

    elif not listen and len(target) and port.isdigit() and 65536 > int(port) > 0:
        client_send(target, int(port), execute)

    elif listen:
        server_loop(int(port), execute)

    else:
        print('Invalid usage: No destination')


main()
