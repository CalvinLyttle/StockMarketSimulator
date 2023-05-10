import argparse
import builtins
import socket

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
    """
    return builtins.print(f"[{colorama.Fore.YELLOW}server\
{colorama.Fore.RESET}]", *args, **kwargs)
     


def main():
    """
    Initializes the multicast group, port, and TTL. Then sends the message
    "robot" to the multicast group.
    """
    TTL = 2

    print(f"Sending multicast message to {GROUP}:{PORT}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)

    sock.sendto(b"robot", (GROUP, PORT))


if "__main__" == __name__:
    """ This is executed when run from the command line """
    main()