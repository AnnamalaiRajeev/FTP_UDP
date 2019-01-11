#!/usr/bin/env python3
# Author : Annamalai Rajeev Chinnikannu  rajeev.chinnikannu@colorado.edu
# name   : Homework 5.2 (Socket_Server)
# purpose: Data Communications Python Assignment
# date   : 30-10-2018
# version: 3.7
#!/usr/bin/env python3
# UDP server on localhost


from cryptography.fernet import Fernet
import ipaddress
import time
import argparse, socket
import re
import os

from datetime import datetime

key = b'-ClO00t5qMSyQPEsdXTVl4lLHWyO4Hn8crdKC41pJoY='
cipher_suite = Fernet(key)

MAX_BYTES = 65535


def get_file(filename_g, address, sock):
    key = b'-ClO00t5qMSyQPEsdXTVl4lLHWyO4Hn8crdKC41pJoY='
    cipher_suite = Fernet(key)
    filename = filename_g.group(1)
    try:
        with open(filename, 'rb') as rf:
            total_file_size = rf.read()
            length = str(len(total_file_size))
            length = length.encode()
            rf.seek(0)
            file_buffer = rf.read(40000)
            print('File Transfer to Client Initiated')
            message_to_client0 = ('Your command{!r} received.File Found ..Your file data is {} bytes long '
                                  'File Found'.format(filename_g.group(0), len(total_file_size)))
            message_to_client0 = message_to_client0.encode()
            filename = filename.encode()
            data_to_client0 = filename + b'|||' + file_buffer + b'|||' + message_to_client0 + b'|||' + length
            data = data_to_client0
            data = cipher_suite.encrypt(data)
            time.sleep(0.001)
            sock.sendto(data, address)
            file_buffer = rf.read(40000)
            time.sleep(0.01)
            while len(file_buffer) > 0:
                data_to_client0 = file_buffer
                data = data_to_client0
                data = cipher_suite.encrypt(data)
                sock.sendto(data, address)
                file_buffer = rf.read(40000)
                time.sleep(0.005)
            print("File transfer complete")

    except FileNotFoundError:
        message_to_client1 = ("The file name doesnt exist.Your message {!r} "
                              "received.FILE NOT FOUND".format(filename_g.group(0)))
        data_to_client1 = message_to_client1
        data = data_to_client1.encode()
        data = cipher_suite.encrypt(data)
        sock.sendto(data, address)
        print("File not Found message sent to client")

    except OSError:
        message_to_client1 = ("Error with Filename.Your message {!r} "
                              "received.FILE NOT FOUND".format(filename_g.group(0)))
        data_to_client1 = message_to_client1
        data = data_to_client1.encode()
        data = cipher_suite.encrypt(data)
        sock.sendto(data, address)
        print("File not Found message sent to client")


def put_file(filename_p, data, address, sock, length_binary):

    key = b'-ClO00t5qMSyQPEsdXTVl4lLHWyO4Hn8crdKC41pJoY='
    cipher_suite = Fernet(key)
    no_of_bytes = length_binary.decode()
    no_of_bytes = int(no_of_bytes)
   
    filename = filename_p.group(1)
    try:
        len_main_data = len(data)
        
        with open(filename, 'wb') as wf:
            wf.write(data)
        while len_main_data < no_of_bytes:
            sock.settimeout(8)
            data1, address = sock.recvfrom(MAX_BYTES)
            sock.settimeout(None)
            data1 = cipher_suite.decrypt(data1)
            with open(filename, 'ab') as wf:
                wf.write(data1)
            len_main_data += len(data1)


        print("file {!r} put in place successfully".format(filename))
        message_to_client0 = ('Your message {!r} received--> File Put in Server Directory --> '
                              'Your file data is {} bytes long '.format(filename_p.group(0), len_main_data))
        message_to_client0 = message_to_client0.encode()
        data_to_client0 = message_to_client0 + b'|||'
        data = data_to_client0
        data = cipher_suite.encrypt(data)
        sock.sendto(data, address)
        print("Process Complete")

    except socket.timeout:
        message_to_client1 = ("Your message {!r} received.FILE CANNOT be Written ".format(filename_p.group(0)))
        data_to_client1 = message_to_client1
        data = data_to_client1.encode()
        time.sleep(0.001)
        data = cipher_suite.encrypt(data)
        sock.sendto(data, address)
        print("File not Found message sent to client")

    except OSError as err:
        print("OS error: {0}".format(err))
        message_to_client1 = ("Your message {!r} received.FILE CANNOT be Written ".format(filename_p.group(0)))
        data_to_client1 = message_to_client1
        data = data_to_client1.encode()
        time.sleep(0.001)
        data = cipher_suite.encrypt(data)
        sock.sendto(data, address)
        print("File not Found message sent to client")


def lister(sock, address):


    key = b'-ClO00t5qMSyQPEsdXTVl4lLHWyO4Hn8crdKC41pJoY='
    cipher_suite = Fernet(key)
    list_of_files = os.listdir()
    list_of_files.remove(os.path.basename(__file__))
    l = str(len(list_of_files))
    data = l.encode()
    data = cipher_suite.encrypt(data)
    sock.sendto(data, address)

    time.sleep(.001)
    for file_name in list_of_files:
        data = file_name.encode()
        data = cipher_suite.encrypt(data)
        sock.sendto(data, address)
        time.sleep(0.0001)
    print("Directory details sent to Client\n")


def server(port, ip_1):

    while True:
        key = b'-ClO00t5qMSyQPEsdXTVl4lLHWyO4Hn8crdKC41pJoY='
        cipher_suite = Fernet(key)
        bravo = 'nogo'
        try:
            #print("yes")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((ip_1, port))
            print('Listening To Global at {}'.format(sock.getsockname()))
            data_t, address_t = sock.recvfrom(MAX_BYTES)
            try:
                data_t = cipher_suite.decrypt(data_t).decode()
            except UnicodeDecodeError:
                print("Improper connection attempt made by client")
            if data_t == 'test':
                time.sleep(0.002)
                data_t = b'The server is active on this line.Link will expire with 30 Sec of Inactivity'
                data_t = cipher_suite.encrypt(data_t)
                sock.sendto(data_t, address_t)

                print("connection attempt by client  {!r} Succesfull".format(address_t))
                bravo = 'go'
            else:
                bravo = 'nogo'

            sock.close()

        except OSError:
            print("Port already in use Please re-enter new port number")
            sock.close()
            break

        if bravo == 'go':

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.bind((ip_1, port))
                sock.settimeout(30)
                print('Listening at {} for client {}'.format(sock.getsockname(), address_t))
                print("Link Established with client {} \n For Security Reasons The Link is active on this line only for the next 30 Seconds to receive a "
                      "command from client".format(address_t))

                data, address = sock.recvfrom(MAX_BYTES)
                sock.settimeout(None)
                data = cipher_suite.decrypt(data)
                text = data.split(b'|||')
                print('The client at {} says {!r}'.format(address, text[0].decode()))
                filename_g = re.search(r'get<(.*)>', text[0].decode())
                filename_p = re.search(r'put<(.*)>', text[0].decode())
                filename_list = re.search(r'--list', text[0].decode())

                if filename_g:

                    get_file(filename_g, address, sock)
                elif filename_p:
                    data_binary = text[1]
                    lenght_binary = text[2]
                    put_file(filename_p, data_binary, address, sock, lenght_binary)
                elif filename_list:
                    lister(sock, address)

                else:

                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    print("file operation not selected ")
                    message_to_client2 = 'The time is {} .Incorrect syntax for fetching the file'.format(datetime.now())
                    message_to_client2 = message_to_client2.encode()
                    data_to_client2 = message_to_client2 + b'|||'
                    data = data_to_client2  # convert to utf-8
                    data = cipher_suite.encrypt(data)
                    sock.sendto(data, address)  # send message to client
                    print("'File operation not identified' message sent to client")
                    sock.close()
            except (OSError, FileNotFoundError):
                print(" Link terminated with Client")

            sock.close()
        elif bravo == 'nogo':
            print('Connection by client attempt failed')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Initiate Server to Send and receive UDP locally.Default IP 127.0.0.1')

    parser.add_argument('port', help='UDP port of Server', type=int, default=1060)
    parser.add_argument('-I', "--IP", metavar='IP ADDRESS', type=str, default='127.0.0.1',

                        help='Enter the Server IP address')
    args = parser.parse_args()

    try:
        ip = ipaddress.ip_address(args.IP)
        server(args.port, args.IP)
    except ValueError:
        print("invalid IP please try again")
