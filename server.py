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

# Disable traceback when exiting with Ctrl+C
sys.tracebacklimit = 0

# Check CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--group",    type=str, help="multicast group")
parser.add_argument("-p", "--port",     type=int, help="multicast port number")
parser.add_argument("-u", "--udp",      type=int, help="UDP port number")
parser.add_argument("-i", "--ip",       type=str, help="TCP IP address")
parser.add_argument("-t", "--tcp",      type=int, help="TCP port number")
args = parser.parse_args()

# Define constants
GROUP = args.group if args.group else '224.1.1.1'   # Default multicast group
MULTICAST_PORT = args.port if args.port else 5000   # Default mutlicast port number
UDP_PORT = args.udp if args.udp else 5001           # Default UDP port number
TCP_IP = args.ip if args.ip else '127.0.0.1'        # Default TCP IP address
TCP_PORT = args.tcp if args.tcp else 5002           # Default TCP port number
RECORDS = []                                        # List of trade records

if MULTICAST_PORT < 1024 or MULTICAST_PORT > 65535:
    print("Mutlicast port number must be between 0 and 65535")
    sys.exit(1)
    
if UDP_PORT < 1024 or UDP_PORT > 65535:
    print("UDP port number must be between 0 and 65535")
    sys.exit(1)
    
if TCP_PORT < 1024 or TCP_PORT > 65535:
    print("TCP port number must be between 0 and 65535")
    sys.exit(1)
    
    
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
    - Initializes the multicast and unicast sockets.
    - Waits for clients to issue buy/sell commands over unicast.
    - Adds the trade record to the RECORDS list.
    - Broadcasts updates to all clients over multicast with a sequence number.
    
    @return: None
    """
    print(f"Ready to send multicast messages to {GROUP}:{MULTICAST_PORT}")
    
    TTL = 2
    broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 
                                   socket.IPPROTO_UDP)
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
            
            print(f"Received request to {message['action']} {message['stock']} \
at {message['price']} from client {message['client']}. Broadcasting to group...")
            
            RECORDS.append(message)
            broadcast_sock.sendto(json.dumps(message).encode('utf-8'), 
                                  (GROUP, MULTICAST_PORT))

def send_tcp():
    """
    Basic server functionality:
    - Recieve TCP connections from clients with a sequence number.
    - Look up the trade record for that sequence number.
    - Send the client that sequence number's trade record.
    
    @return: None
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
