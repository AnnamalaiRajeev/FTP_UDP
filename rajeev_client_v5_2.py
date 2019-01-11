#!/usr/bin/env python3
# Author : Annamalai Rajeev Chinnikannu  rajeev.chinnikannu@colorado.edu
# name   : Homework 5.2 (Socket_Client)
# purpose: Data Communications Python Assignment
# date   : 30-10-2018
# version: 3.7
#!/usr/bin/env python3
# UDP server on localhost

import sys
import ipaddress
import re
import time
import argparse, socket
from cryptography.fernet import Fernet


key = b'-ClO00t5qMSyQPEsdXTVl4lLHWyO4Hn8crdKC41pJoY='   # declare global key
cipher_suite = Fernet(key)
MAX_BYTES = 64000


def get_file(filename, ip1, port):

    try:
        print("The File name entered by you is : {}".format(filename.group(1)))
        filename = filename.group(0).encode()
        message = filename+b'|||'                    # initial message to server

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        datagram = message                          # initial message set to datagram
        datagram = cipher_suite.encrypt(datagram)

        sock.sendto(datagram, (ip1, port))          # initial message sent to server

        print('The OS assigned me the address {}'.format(sock.getsockname()))
        print("started listening")
        sock.settimeout(8)
        data, address = sock.recvfrom(MAX_BYTES)     # Danger open connection # waiting for initial # reply message from server
        sock.settimeout(None)
        print("waiting for file")
        data = cipher_suite.decrypt(data)
        list1 = data.split(b'|||')        # client tries to perform operations based on server message
        if len(list1) == 4:              # client gets the file
                                         # server piggybacks the first data packet on initial messages
            filename = list1[0].decode()
            maindata = list1[1]
            servermessage = list1[2].decode()
            no_of_bytes = list1[3].decode()
            no_of_bytes = int(no_of_bytes)
            print('The server {} replied {!r}'.format(address, servermessage))
            len_main_data = len(maindata)
            data_n = b''
            with open(filename, 'wb') as wf:
                wf.write(maindata)
            while len_main_data < no_of_bytes:
                sock.settimeout(8)
                data1, address = sock.recvfrom(MAX_BYTES)
                sock.settimeout(None)
                len_main_data += len(data1)
                data_n += data1
                print("Percent completed {}".format((len_main_data/no_of_bytes)*100))
            #    if len(data_n) >= 100000:
            data_n = cipher_suite.decrypt(data_n)
            with open(filename, 'ab') as wf:
                wf.write(data_n)
                print("written File")


            print("File Received")

        elif len(list1) == 2:                            # executes if this if there is syntax mismatch between
                                                         # the client and server
            servermessage2 = list1[1].decode()
            print('The server {} replied {!r}'.format(address, servermessage2))
        elif len(list1) == 1:                             #  executes if file not found in server
            servermessage1 = list1[0].decode()
            print('The server {} replied {!r}'.format(address, servermessage1))
        else:
            print("error")

    except socket.timeout:

        print("Unable to Get File.Error in Writing file..Attempting reconnect to server ")
    except OSError as err:
        print("OS error: {0}".format(err))

    sock.close()


def put_file(filename, ip1, port):

    print("The File name entered by you is : {}".format(filename.group(1)))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        with open(filename.group(1), 'rb') as rf:
            print("File Exists in Client Directory. \t Put Operation Initiated ")
            length = str(len(rf.read()))

            length = length.encode()

            rf.seek(0)
            file_buffer = rf.read(40000)

            filename = filename.group(0).encode()
            data_to_server0 = filename + b'|||' + file_buffer + b'|||' + length
            datagram = data_to_server0
            datagram = cipher_suite.encrypt(datagram)
            sock.sendto(datagram, (ip1, port))
            file_buffer = rf.read(40000)
            while len(file_buffer) > 0:
                data_to_client0 = file_buffer
                datagram = data_to_client0
                time.sleep(0.08)
                datagram = cipher_suite.encrypt(datagram)
                sock.sendto(datagram, (ip1, port))
                file_buffer = rf.read(40000)

            print("File Data Transferred to Server Success\n listening Initiated, waiting "
                  "for Transfer Status from Server")

            sock.settimeout(8)
            data, address = sock.recvfrom(MAX_BYTES)  # Danger open connection
            sock.settimeout(None)
            data = cipher_suite.decrypt(data)
            list1 = data.split(b'|||')
            servermessage = list1[0].decode()
            print('The server {} replied {!r}'.format(address, servermessage))

    except FileNotFoundError:
        print("File {!r} NOT FOUND in client Directory".format(filename.group(1)))
    except socket.timeout:
        print("No Reply from Server: Connection Error Detected \n "
              ".Operation  state : 'Failed'..Please check for active Link")
    except OSError as err:
        print("OS error: {0}".format(err))
    sock.close()


def lister(filename_l, ip1, port):

    try:
        print("The command entered by you is : {}".format(filename_l.group(0)))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        filename_l = filename_l.group(0).encode()
        data_to_server0 = filename_l + b'|||'
        datagram = data_to_server0
        datagram = cipher_suite.encrypt(datagram)
        sock.sendto(datagram, (ip1, port))
        sock.settimeout(8)
        data1, address = sock.recvfrom(MAX_BYTES)
        sock.settimeout(None)
        data1 = cipher_suite.decrypt(data1)
        l = data1.decode()
        length = int(l)
        ret_list = []
        while length > 0:
            data1, address = sock.recvfrom(MAX_BYTES)
            data1 = cipher_suite.decrypt(data1)
            data1 = data1.decode()
            ret_list.append(data1)
            length = length-1
        print('the List of all the files in the server directory are\n {}'.format(ret_list))
    except socket.timeout:
        print("unable to Retrieve List.. Connection with Server Failed...attempting reconnection with server")
    except OSError as err:
        print("OS error: {0}".format(err))

    sock.close()


def client(ip1, port):

    key = b'-ClO00t5qMSyQPEsdXTVl4lLHWyO4Hn8crdKC41pJoY='
    cipher_suite = Fernet(key)

    while True:
        bravo = 'nogo'

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # attempting connection to server
            test = b'test'
            test = cipher_suite.encrypt(test)
            time.sleep(0.5)
            sock.sendto(test, (ip1, port))
            sock.settimeout(8)
            data_t, address_t = sock.recvfrom(MAX_BYTES)
            sock.settimeout(None)
            sock.close()
            text = b'The server is active on this line.Link will expire with 30 Sec of Inactivity'
            if cipher_suite.decrypt(data_t) == text:
                print("Link to Server Successfully Re-Established \n")
                data_t = cipher_suite.decrypt(data_t).decode()
                print("The Server Says {!r}".format(data_t))
                bravo = 'go'
            else:
                bravo = 'nogo'
        except OSError:
            print("No active Server Listening on Socket ({},{})".format(ip1, port))

        if bravo == 'go':

            filename = input("********************Client Options********************************************"
                             "******************\n"
                             "Enter the get command in the format \n"
                             " 'get<filename>' : Gets the file by transferring the file 'filename' "
                             "from server directory into client directory.: \n"
                             " 'put<filename>': Upon entering this option at client,client puts the file 'filename' in "
                             "server directory.\n "
                             "'exit': Upon entering this option, the client will  exit and free all the scokets  "
                             "that were created on client.\n"""
                             "'--list': Upon entering this option, client will fetch the list of files present in"
                             " the server directory"
                             "\n" + "Link REFRESHED.{} \n Enter Command to Perform Operation || "
                                                      "Enter any key to ".format(data_t) +
                             "refresh link\n")


            filename_g = re.search(r'get<(.*)>', filename)
            filename_p = re.search(r'put<(.*)>', filename)
            filename_l = re.search(r'--list', filename.lower())
            exiter = re.search(r'exit', filename.lower())
            if exiter:
                print("all Sockets  created are now safely closed.\n The Program will now  exit")
                time.sleep(1)
                print("THANK YOU")
                break
            elif filename_g:
                get_file(filename_g, ip1, port)
            elif filename_p:
                put_file(filename_p, ip1, port)
            elif filename_l:
                lister(filename_l, ip1, port)
            else:
                print("The Format  entered by you  : {!r}  is not a proper command".format(filename))
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # attempting connection to server
                test = b'test'
                test = cipher_suite.encrypt(test)
                sock.sendto(test, (ip1, port))
                time.sleep(0.001)

        elif bravo == 'nogo':

            print("No Go from Server.Server Unreachable \nAttempting Reconnection with Server at '{},{}'".format(ip1, port))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Send and receive UDP locally')

    parser.add_argument('PORT', help="input the destination port ", type=int)

    parser.add_argument('IP', help='Enter the Server IP address', type=str)
    args = parser.parse_args()
    alpha = 'nogo'
    try:
        ip = ipaddress.ip_address(args.IP)
        alpha = 'go'

    except ValueError:

        print("invalid IP please try again")
    if alpha == 'go':
        client(args.IP, args.PORT)