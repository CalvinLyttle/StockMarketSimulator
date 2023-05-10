import argparse
import builtins
import json
import math
import random
import socket
import struct
import sys
import threading
import time

import colorama

"""
This is the client side of the multicast communication. It receives the
multicast messages and prints them to the console.
"""

__authors__ = "Ari Birnbaum, Calvin Lyttle, Grace Mattern, and Kevin Ha"
__version__ = "0.1.0"
__license__ = "MIT"

# Check if the client number or port number was specified
# Use the default values if they were not specified
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--client", type=int, help="client number")
parser.add_argument("-p", "--port", type=int, help="port number")
parser.add_argument("-g", "--group", type=str, help="multicast group")
args = parser.parse_args()

CLIENT_NUM = args.client if args.client else 0
PORT = args.port if args.port else 5000
GROUP = args.group if args.group else '224.1.1.1'

if CLIENT_NUM < 0 or CLIENT_NUM > 10000:
    print("Client number must be between 0 and 10000")
    sys.exit(1)
if PORT < 1024 or PORT > 65535:
    print("Port number must be between 0 and 65535")
    sys.exit(1)

# UDP Multicast Socket
broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
broadcast_sock.bind((GROUP, PORT))

mreq = struct.pack("4sl", socket.inet_aton(GROUP), socket.INADDR_ANY)
broadcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# UDP Unicast Socket
# TODO: Turn this into unicast socket
UDP_PORT = PORT + 1
unicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# TCP Socket
# TODO: Ensure this is a TCP socket
TCP_PORT = PORT + 2
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_sock.bind((GROUP, TCP_PORT))

actions = [
    {
        "client": CLIENT_NUM,
        "action": "BUY",
        "stock": "AAPL",
        "price": 170.20
    },
    {
        "client": CLIENT_NUM,
        "action": "SELL",
        "stock": "AMZN",
        "price": 109.32
    }
]

def print(*args, **kwargs):
    """
    This is a wrapper around the built-in print function that adds the
    client number to the beginning of the message.
    
    @param args: The arguments to pass to the print function.
    @param kwargs: The keyword arguments to pass to the print function.
    @return: None
    """
    return builtins.print(f"[{colorama.Fore.GREEN}client-{CLIENT_NUM}\
{colorama.Fore.RESET}]", *args, **kwargs)
                          

def send():
    """
    This sends a random trade action to the server over
    UDP unicast every 1-10 seconds.
    
    @return: None
    """
    while True:
        action = random.choice(actions)
        print(f"Sending request to {action['action']} \
{action['stock']} at ${action['price']} to server...")
        message = json.dumps(action).encode('utf-8')
        unicast_sock.sendto(message, (GROUP, UDP_PORT))
        time.sleep(math.floor(random.random() * 10) + 1)

def recv():
    """
    This initializes the multicast group and port. Then it listens for
    multicast messages and prints them to the console.
    
    @return: None
    """  
    print(f"Listening for multicast messages on {GROUP}:{PORT}")

    while True:
        data = broadcast_sock.recv(1024).decode('utf-8')

        if data:
            try:
                message = json.loads(data)
                print(f"Recieved broadcast that client {message['client']} issued \
{message['action']} {message['stock']} at ${message['price']}")
            except json.decoder.JSONDecodeError:
                print("Received invalid JSON message")
                continue
            
            # Check for sequence number
            # if message["seq"] == seq:
            #     print(f"Received message: {message}")
            #     seq += 1
            # else:
            #     print(f"Received out-of-order message: {message}")
            #     # TODO: TCP connection to request retransmission
                

if "__main__" == __name__:
    """ This is executed when run from the command line """

    # Init two sockets, one for receiving multicast messages, one for sending trade requests
    recv_socket = threading.Thread(target=recv)
    send_socket = threading.Thread(target=send)
    
    try:
        # Start both sockets
        recv_socket.start()
        send_socket.start()

    except KeyboardInterrupt:
        sys.exit(0)

