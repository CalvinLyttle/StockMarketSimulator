#!/usr/bin/env bash

# Authors: Ari Birnbaum, Calvin Lyttle, Grace Mattern, and Kevin Ha
# Version: 0.1.0
# License: MIT

TXT_DEFAULT='\033[0m'
TXT_GREY='\033[2m'

# Kill all processes on Ctrl-C
handle_sigint() {
    echo -e "[${TXT_GREY}init${TXT_DEFAULT}] Killing server and clients..."
    # shellcheck disable=SC2046
    kill $(jobs -p) >/dev/null 2>&1
    echo -e "[${TXT_GREY}init${TXT_DEFAULT}] Done."
    exit 0
}

trap 'handle_sigint' INT

# Check if Python 3 is installed
if ! command -v python3 >/dev/null; then
    echo -e "[${TXT_GREY}init${TXT_DEFAULT}] Python 3 is not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip >/dev/null; then
    echo -e "[${TXT_GREY}init${TXT_DEFAULT}] pip is not installed."
    exit 1
fi

# Default values
NUM_CLIENTS=9
PORT=5000
GROUP="224.1.1.1"

# Parse command line arguments
# -c | --clients <num_clients>
# -p | --port <port>
# -h | --help
while getopts 'c:p:g:h' flag; do
    case "${flag}" in
    c) NUM_CLIENTS="${OPTARG}" ;;
    p) PORT="${OPTARG}" ;;
    g) GROUP="${OPTARG}" ;;
    h)
        echo "Usage: $0 [-c <num_clients>] [-p <port>] [-g <x.x.x.x>] [-h]"
        exit 0
        ;;
    *)
        echo "Usage: $0 [-c <num_clients>] [-p <port>] [-g <x.x.x.x>] [-h]"
        exit 1
        ;;
    esac
done

# Install dependencies
pip install -r requirements.txt >/dev/null

# Run server in background
echo -e "[${TXT_GREY}init${TXT_DEFAULT}] Starting server..."
python server.py -p "$PORT" -g "$GROUP" &

# Run multiple clients in the background
echo -e "[${TXT_GREY}init${TXT_DEFAULT}] Starting ${NUM_CLIENTS} clients..."
for i in $(seq 1 "$NUM_CLIENTS"); do
    if [ "$i" -eq "$NUM_CLIENTS" ]; then
        # Run last client in the foreground
        python client.py -c "$i" -p "$PORT" -g "$GROUP"
        continue
    fi
    python client.py -c "$i" -p "$PORT" -g "$GROUP" &
done
