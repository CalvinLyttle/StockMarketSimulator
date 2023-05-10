import argparse
import builtins
import json
import socket
import sys
import threading

import colorama

"""
This is the server side of the multicast communication. It sends the
multicast messages to the clients.
"""

__authors__ = "Ari Birnbaum, Calvin Lyttle, Grace Mattern, and Kevin Ha"
__version__ = "0.1.0"
__license__ = "MIT"

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int, help="port number")
parser.add_argument("-g", "--group", type=str, help="multicast group")
args = parser.parse_args()

TCP_IP = '127.0.0.1'
PORT = args.port if args.port else 5000
GROUP = args.group if args.group else '224.1.1.1'
RECORDS = []

if PORT < 1024 or PORT > 65535:
    print("Port number must be between 0 and 65535")
    sys.exit(1)
    
UDP_PORT = PORT + 1
TCP_PORT = PORT + 2

def print(*args, **kwargs):
    """
    This is a wrapper around the built-in print function that adds the
    server to the beginning of the message.
    
    @param args: The arguments to pass to the print function.
    @param kwargs: The keyword arguments to pass to the print function.
    @return: None
    """
    return builtins.print(f"[{colorama.Fore.YELLOW}server\
{colorama.Fore.RESET}]", *args, **kwargs)
     


def send_udp():
    """
    Basic server functionality:
    - Initializes the multicast group, port, and TTL. 
    - Sends the message "server online" to the multicast group.
    - Waits for clients to issue buy/sell commands.
    - Broadcasts updates to all clients.
    
    @return: None
    """
    print(f"Ready to send multicast messages to {GROUP}:{PORT}")
    TTL = 2
    broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broadcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
    
    unicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    unicast_sock.bind((GROUP, UDP_PORT))

    seq = 0
    while True:
        data = unicast_sock.recv(10240)
        
        if data:
            try :
                message = json.loads(data.decode('utf-8'))
            except json.decoder.JSONDecodeError:
                print("Received invalid JSON message")
                continue
            
            message["seq"] = seq
            seq += 1
            
            print(f"Recieved request to {message['action']} {message['stock']} \
at {message['price']} from client {message['client']}. Broadcasting to group...")
            
            # message["action"]
            # message["stock"]
            # message["price"]
            
            RECORDS.append(message)
            broadcast_sock.sendto(json.dumps(message).encode('utf-8'), (GROUP, PORT))

def send_tcp():
    """
    Basic server functionality:
    - Recieve TCP connections from clients with a sequence number.
    - Send the client that sequence number's trade record.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((TCP_IP, TCP_PORT))
    sock.listen(1)
    print(f'Ready to recieve TCP fallback requests on {TCP_IP}:{TCP_PORT}')

    while True:
        connectionSocket, addr = sock.accept()
        data = connectionSocket.recv(1024).decode('utf-8')
        message = json.loads(data)
        seq = message["seq"]
        resp_dict = RECORDS[seq]
        resp_dump = json.dumps(resp_dict)
        
        connectionSocket.send(resp_dump.encode())
        connectionSocket.close()


if "__main__" == __name__:
    """ This is executed when run from the command line """
    
    # Initialize the TCP and UDP threads
    send_udp_thread = threading.Thread(target=send_udp)
    send_tcp_thread = threading.Thread(target=send_tcp)
    
    try:
        # Start both the UDP and TCP threads
        send_udp_thread.start()
        send_tcp_thread.start()
        
    except KeyboardInterrupt:
        send_udp_thread.join()
        send_tcp_thread.join()
        sys.exit(0)
