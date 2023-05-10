# CS-521 Group Project - Stock Market Simulator

### Stevens Institute of Technology, Spring 2023

I pledge my honor that I have abided by the Stevens Honor System.

For our project, we will be creating a simulation of a stock market. This will involve one central server (the market) and several listeners (traders, news media, etc.).

The server will send out multicast UDP messages to all listeners with a sequence number. The sequence number will tell the listeners whether they have missed a message if the number is higher than what they are expecting.

The messages the server sends out will come from messages it receives from the clients like buy or sell orders. If a client misses a message, they will tell the server and will establish a TCP connection to guarantee the transmission with acknowledgements.

Authors:

-   Ari Birnbaum
-   Calvin Lyttle
-   Grace Mattern
-   Kevin Ha

## Getting Started

Start by installing the required packages:

```bash
# Initialize virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

Then, run the init script to run the server and clients:

```bash
# To run the server and 10 clients on port 5000:
bash init.sh

# To run the server and 5 clients on port 3000:
bash init.sh -c 5 -p 3000
```

**Note**: We recommend running this on a Linux machine.

## Credits

Initial stock data was taken from [this Kaggle dataset](https://www.kaggle.com/datasets/camnugent/sandp500).
