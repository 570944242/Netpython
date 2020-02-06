#!/usr/bin/python3

import sys
import time
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
order = False
scan = False
dns = True
file = None
delay = 0
allp = {'25' : 'smtp',
        '80' : 'http',
        '443': 'https',
        '20' : 'ftp',
        '21' : 'ftp',
        '23' : 'telnet',
        '143': 'imap',
        '3389': 'rdp',
        '22' : 'ssh',
        '53' : 'dns',
        '67' : 'dhcp',
        '68' : 'dhcp',
        '110': 'pop3'}

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

    print("""[V1.10 github.com/hackerSMinh/Netpython]
Connect: np.py -t hostname -p port[s] [-options]
Listen:  np.py -l -p port [-options]
Scan:    np.py -t hostname -p min_port-max_port -z [-options]
Options:""")

    print("       -h                     This help")
    print("       -l                     Listen for inbound connects")
    print("       -L                     Re-listen after disconnect")
    print("       -p port[s]             Port for the connection")
    print("       -e file                Execute program upon connection")
    print("       -c                     Use `-e` as '/bin/bash' in unix and 'cmd' in windows")
    print("       -t addr                Host for the ibound connection")
    print("       -n                     No DNS lookup, only IP addresses")
    print("       -u                     UDP protocol mode")
    print("       -r                     Random local or remote ports")
    print("       -o file                Dump of traffic (can't used with `-e` or `-c`)")
    print("       -d secs                Delay interval for lines sent")
    print("       -k                     Keep socket alive")
    print("       -v                     Verbose mode")
    print("       -V                     More verbose")
    print("       -w secs                Set timeout for the socket")
    print("       -C                     CLRF as line ending ")
    print("       -z                     Zero I/O mode (used in port scaning)")
    print("       -O                     Ordinarily I/O mode (used in backdoor shell to avoid some I/O errors)")
    print("       -P pass                Require password to connects")
    print("       -N name                Your name as the first line (for recognize when chating)")
    print("       -b                     Display the Netpython banner")
    print("Port numbers can be individual or ranges: min-max; netpython commands are also support HTTP requests")

    sys.exit(0)


def dump():
    global dump
    if file != None:
        try:
            dump = open(file, 'w')
            dump.write(time.asctime(time.localtime(time.time())) + '\n\n')
        except:
            print("Can't dump to file %s" % file)
            quit()


def o(s):
    while 1:
        try:
            data = ''
            while 1:
                packet = s.recv(1024)
                data += packet.decode()
                if file != None:
                    for x in packet.decode().split('\n'):
                        dump.write('< %s' % x)
                if len(packet) < 1024:
                    break
            print(data, end='')
            if not len(data):
                s.close()
                break
        except:
            s.close()
            break


def exec_command(command, exe):
    command = command.rstrip()

    try:
        if exe == 'cmd' or 'cmd.exe' in exe or exe == '/bin/bash' or exe == '/bin/sh':
            if command == 'help':
                if sys.platform == 'win32':
                    f = 'help.wd'
                else:
                    f = 'help.ln'
                out = open(f, 'r').read()
            else:
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
            if file != None:
                dump.write('> Enter the password:')
            pw = client_socket.recv(1024).decode().replace('\n', '')
            if file != None:
                dump.write('< %s' % pw) 
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
            path = os.getcwd()
            if '/home/%s' % usr in path and usr != 'root':
                path = path.replace('/home/%s' % usr, '~')
            client_socket.send(('\n%s@%s:%s%s ' % (usr, socket.gethostname(), path, end)).encode())
        else:
            client_socket.send(b'\n')

        while 1:
            try:
                cmd_buffer = client_socket.recv(1024)

                _str = cmd_buffer.decode().replace('\n', '')
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
                        path = os.getcwd()
                        if '/home/%s' % usr in path and usr != 'root':
                            path = path.replace('/home/%s' % usr, '~')
                        client_socket.sendall(out + ('%s@%s:%s%s ' % (usr, socket.gethostname(), path, end)).encode())

                else:
                    out = exec_command(_str, execute)
                    client_socket.send(out + b'\n')

            except:
                client_socket.close()
                break


    else:
        if name != None:
            client_socket.send(b'[%s]\n' % name)
            if file != None:
                dump.write('> [%s]\n' % name)
        if order == False:
            _thread = threading.Thread(target=o, args=[client_socket])
            _thread.start()
                
        while 1:
            try:
                if order == True:
                    data = ''
                    while 1:
                        packet = client_socket.recv(1024)
                        data += packet.decode()
                        if len(packet) < 1024:
                            break
                        if file != None:
                            for x in packet.decode().split('\n'):
                                dump.write('< %s' % x)
                    print(data, end='')
                    if not len(data):
                        client_socket,close()
                        break
                    if file != None:
                        dump.write('< %s' % data)
                buffer = input('') + '\n'
                if file != None:
                    dump.write('> %s' % buffer)
                if int(port) in (80, 443):
                    i = 0
                    while 1:
                        data = input()
                        buffer += data + '\n'
                        if file != None:
                            dump.write('> %s\n' % data)
                        if data == '':
                            i += 1
                        if i == 1:
                            break
                    while 1:
                        data = input()
                        buffer +=  data + '\n'
                        if file != None:
                            dump.write('> %s\n' % data)
                        if data == '':
                            i += 1
                        if i == 2:
                            break
                        
                if clrf == True:
                    buffer += '\n'
                if delay != 0:
                    time.sleep(int(delay))
                client_socket.send(buffer.encode())

            except KeyboardInterrupt:
                print('^C')
                client_socket.close()
                break

            except:
                client_socket.close()
                break


def client_connect(target, port, exe):
    if dns:
        try:
            h = socket.gethostbyname(target)
            lookup = socket.gethostbyaddr(h)
            hostname = lookup[0]
            ip = lookup[2][0]
            if target == 'localhost':
                ip = '127.0.0.1'
            if mver == True:
                if target == hostname:
                    print('DNS (forward/reverse) match: %s == %s' % (target, hostname))
                else:
                    print('DNS (forward/reverse) mismatch: %s != %s' % (target, hostname))
        except:
            print('[%s]: Host lookup failed: unknown host' % target)
            quit()
    else:
        try:
            socket.inet_aton(target)
            ip = target
        except:
            print('%s is not an IP adrress' % target)
            quit()
    try:
        client = socket.socket(socket.AF_INET, typ)
        if timeout != None:
            client.settimeout(int(timeout))
        host = target
        if ip == target:
            host = '(UNKNOWN)'
        client.connect((ip, port))
            
        if ver == True or mver == True:
            try:
                print('%s [%s] %s (%s): Open' % (host, ip, port, allp[str(port)]))
            except:
                print('%s [%s] %s (?): Open' % (host, ip, port))
        if alive == True:
            client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if zero == True:
            client.close()

        else:
            try:
                client_handler(client, exe, pwd)
            except KeyboardInterrupt:
                print('^C')

    except socket.error as msg:
        msg = str(msg)
        if 'getaddrinfo failed' in msg:
            print('[%s]: Host lookup failed: unknown host' % target)
            quit()
        elif '10061' in msg and (mver == True or scan == False):
            try:
                print('%s [%s] %s (%s): Connection refused' % (host, ip, port, allp[str(port)]))
            except:
                print('%s [%s] %s (?): Connection refused' % (host, ip, port))
        elif '104' in msg and (mver == True or scan == False):
            try:
                print('%s [%s] %s (%s): Connection reset' % (host, ip, port, allp[str(port)]))
            except:
                print('%s [%s] %s (?): Connection reset' % (host, ip, port))
        elif '104' in msg and (mver == True or scan == False):
            try:
                print('%s [%s] %s (%s): Connection timeout' % (host, ip, port, allp[str(port)]))
            except:
                print('%s [%s] %s (?): Connection timeout' % (host, ip, port))         
        elif mver == True:
            try:
                print('%s [%s] %s (%s): Connection failed' % (host, ip, port, allp[str(port)]))
            except:
                print('%s [%s] %s (?): Connection failed' % (host, ip, port))


def server_listen(port, exe):
    target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, typ)
    try:
        server.bind((target, port))
    except:
        print("Can't bind at [0.0.0.0] %s" % port)
        quit()

    if ver == True or mver == True:
        print('Listening on %s ...' % port)

    server.listen(5)
    if timeout != None:
        client.settimeout(int(timeout))

    try:
        client_socket, addr = server.accept()
        if alive == True:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        if ver == True or mver == True:
            print('(UNKNOWN) [%s] %s : Connection succeeded' % (addr[0], addr[1]))

        client_handler(client_socket, exe, pwd)


    except KeyboardInterrupt:
        print('^C')


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
    global order
    global scan
    global dns
    global delay
    global file

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlLe:t:p:zvurw:d:cCN:kVbOnd:o:", ["help", "listen", "execute",
                                                        "target", "port", "zero", "verbose", "udp",
                                                        "random", "timeout", "passwd", "terminal",
                                                        "clrf", "name", "keepalive", "Mverbose", "banner"
                                                        "order", "ip", "delay", "file"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h"):
            usage()
        elif o in ("-l"):
            listen = True
        elif o in ("-L"):
            listen = [True, True] 
        elif o in ("-e"):
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
        elif o in ("-o", "o"):
            file = a
        elif o in ("-P", "P"):
            pwd = a
        elif o in ("-c", "c"):
            if sys.platform == 'win32':
                execute = 'cmd'
            else:
                execute = '/bin/sh'
        elif o in ("-C", "C"):
            clrf = True
        elif o in ("-N", "N"):
            name = a
        elif o in ("-n", "n"):
            dns = False
        elif o in ("-k", "k"):
            alive = True
        elif o in ("-V", "V"):
            mver = True
        elif o in ("-O", "O"):
            order = True
        elif o in ("-d", "d"):
            delay = a
        elif o in ("-b", "b"):
            print(banner)
            quit()
        else:
            pass

    dump()
    
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
        print("No port[s] (use `-r` to randomize ports)")
        quit()
    if (not port.isdigit() or not 65536 > int(port) > 0) and not '-' in port:
        print('Invalid port %s' % port)
        quit()
    if timeout != None and not timeout.isdigit():
        print('Invalid timeout %s seconds' % timeout)
        quit()
    if not str(delay).isdigit() or int(delay) < 0:
        print('Invalid delay time %s seconds' % delay)
        quit()

    if not listen and len(target) and '-' in port:
        scan = True
        ver = True
        fport = int(port.split('-')[0])
        lport = int(port.split('-')[1])
        for p in range(fport, lport+1):
            _thread = threading.Thread(target=client_connect, args=(target, p, execute))
            _thread.start()

    elif not listen and len(target) and port.isdigit() and 65536 > int(port) > 0:
        client_connect(target, int(port), execute)

    elif listen == True:
        server_listen(int(port), execute)

    elif listen == [True, True]:
        while 1:
            server_listen(int(port), execute)

    else:
        print('No destination')


main()

