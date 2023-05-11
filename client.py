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

# Disable traceback when exiting with Ctrl+C
sys.tracebacklimit = 0

with open('actions.json') as actions_json:
    actions = json.load(actions_json)["actions"]


# Check CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--client",   type=int, help="client number")
parser.add_argument("-g", "--group",    type=str, help="multicast group")
parser.add_argument("-p", "--port",     type=int, help="port number")
parser.add_argument("-u", "--udp",      type=int, help="UDP port number")
parser.add_argument("-i", "--ip",       type=str, help="TCP IP address")
parser.add_argument("-t", "--tcp",      type=int, help="TCP port number")
parser.add_argument("-d", "--drop",     type=int, help="percentage of packets to drop")
args = parser.parse_args()

# Define constants
CLIENT_NUM = args.client if args.client else 0      # Default client number
GROUP = args.group if args.group else '224.1.1.1'   # Default multicast group
MULTICAST_PORT = args.port if args.port else 5000   # Default mutlicast port number
UDP_PORT = args.udp if args.udp else 5001           # Default UDP port number
TCP_IP = args.ip if args.ip else '127.0.0.1'        # Default TCP IP address
TCP_PORT = args.tcp if args.tcp else 5002           # Default TCP port number
DROP = args.drop if args.drop else 10               # Default % of packets to drop


if CLIENT_NUM < 0 or CLIENT_NUM > 10000:
    print("Client number must be between 0 and 10000")
    sys.exit(1)
    
if MULTICAST_PORT < 1024 or MULTICAST_PORT > 65535:
    print("Multicast port number must be between 0 and 65535")
    sys.exit(1)
    
if UDP_PORT < 1024 or UDP_PORT > 65535:
    print("UDP port number must be between 0 and 65535")
    sys.exit(1)
    
if TCP_PORT < 1024 or TCP_PORT > 65535:
    print("TCP port number must be between 0 and 65535")
    sys.exit(1)
    
if DROP < 0 or DROP > 100:
    print("Drop percentage must be between 0 and 100")
    sys.exit(1)


# UDP Multicast Socket
broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
broadcast_sock.bind((GROUP, MULTICAST_PORT))

mreq = struct.pack("4sl", socket.inet_aton(GROUP), socket.INADDR_ANY)
broadcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# UDP Unicast Socket
unicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)


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
        action["client"] = CLIENT_NUM
        
        print(f"Sending request to {action['action']} \
{action['stock']} at ${action['price']} to server...")
        
        message = json.dumps(action).encode('utf-8')
        unicast_sock.sendto(message, (GROUP, UDP_PORT))
        time.sleep(math.floor(random.random() * 10) + 1)
        
def send_tcp_fallback(seq):
    """
    This sends a TCP message to the server requesting a missing trade
    based on the sequence number provided.

    @param seq (int): The sequence number of the missing trade.
    @return: None
    """
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((TCP_IP, TCP_PORT))
    seq_message = json.dumps({
        "client": CLIENT_NUM,
        "seq": seq
    })
    
    tcp_sock.sendall(seq_message.encode('utf-8'))
    data = tcp_sock.recv(1024)
    
    try:
        recieved_message = json.loads(data)
    except json.decoder.JSONDecodeError:
        print("Received invalid JSON message")
    
    print(f"Received missing trade: {recieved_message['action']} \
{recieved_message['stock']} at ${recieved_message['price']} (seq. {seq})")
    tcp_sock.close()

def recv():
    """
    This initializes the multicast group and port. Then it listens for
    multicast messages and prints them to the console.
    
    @return: None
    """  
    print(f"Listening for multicast messages on {GROUP}:{MULTICAST_PORT}")
    
    seq = 0
    while True:
        data = broadcast_sock.recv(1024).decode('utf-8')
        
        # Randomly drop messages, set higher to show > 1 missed packets
        if random.random() < DROP/100:
            print("Simulating dropped message")
            continue

        if data:
            try:
                message = json.loads(data)
                print(f"Recieved broadcast that client {message['client']} issued \
{message['action']} {message['stock']} at ${message['price']}")
            except json.decoder.JSONDecodeError:
                print("Received invalid JSON message")
                continue
            
            if message["seq"] > seq:
                print(f"Received out of order message. \
Expected {seq}, got {message['seq']}")

                # Iterate through just one or all missed packets.
                for miss_seq in range(seq, message['seq']):
                    send_tcp = threading.Thread(send_tcp_fallback(miss_seq))
                    send_tcp.start()
                    seq = message["seq"]
                    send_tcp.join()
                    
            seq += 1


if "__main__" == __name__:
    """ This is executed when run from the command line """

    # Init two sockets, one for receiving multicast messages, 
    # one for sending trade requests
    recv_socket = threading.Thread(target=recv)
    send_socket = threading.Thread(target=send)
    
    try:
        # Start both sockets
        recv_socket.start()
        send_socket.start()

    except KeyboardInterrupt:
        recv_socket.join()
        send_socket.join()
        sys.exit(0)

