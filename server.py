import argparse
import builtins
import socket
import sys
import json

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

PORT = args.port if args.port else 5000
GROUP = args.group if args.group else '224.1.1.1'

if PORT < 1024 or PORT > 65535:
    print("Port number must be between 0 and 65535")
    exit(1)
    


def print(*args, **kwargs):
    """
    This is a wrapper around the built-in print function that adds the
    server to the beginning of the message.
    
    @param args: The arguments to pass to the print function.
    @param kwargs: The keyword arguments to pass to the print function.
    @return: None
    """
    return builtins.print(f"[{colorama.Fore.YELLOW}server-0\
{colorama.Fore.RESET}]", *args, **kwargs)
     


def main():
    """
    Basic server functionality:
    - Initializes the multicast group, port, and TTL. 
    - Sends the message "server online" to the multicast group.
    - Waits for clients to issue buy/sell commands.
    - Broadcasts updates to all clients.
    
    @return: None
    """
    TTL = 2
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)


    while True:
        data = sock.recv(10240)
        if data:
            # print(f"Sending multicast message to {GROUP}:{PORT}")
            
            message = json.loads(data.decode('utf-8'))
            action = message.action
            stock = message.stock
            price = message.price

            message = f"{action} order for {stock} at {price}"
            sock.sendto(message.encode('utf-8'), (GROUP, PORT))



if "__main__" == __name__:
    """ This is executed when run from the command line """
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
