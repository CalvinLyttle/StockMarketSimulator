import argparse
import builtins
import socket
import struct
import sys

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
    exit(1)
if PORT < 1024 or PORT > 65535:
    print("Port number must be between 0 and 65535")
    exit(1)


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
                          

def main():
    """
    This initializes the multicast group and port. Then it listens for
    multicast messages and prints them to the console.
    
    @return: None
    """  
    print(f"Listening for multicast messages on {GROUP}:{PORT}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((GROUP, PORT))
        
    mreq = struct.pack("4sl", socket.inet_aton(GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        # Check sequence number.
        print(sock.recv(10240))

if "__main__" == __name__:
    """ This is executed when run from the command line """
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)

