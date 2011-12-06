# wssh - websocket shell

wssh ("wish") is a command-line utility/shell for WebSocket inpsired by netcat.

## Install

	pip install wssh

## Usage

Listen for WebSocket connections on a particular path and print messages to STDOUT:

	wssh -l localhost:8000/websocket

Once connected you can use STDIN to send messages. Each line is a message. You can just as well open a peristent client connection that prints incoming messages to STDOUT and sends messages from STDIN interactively:

	wssh localhost:8000/websocket

You can also connect using secure WebSocket by using a full URI (assuming the server accepts it):

	wssh wss://localhost:8000/websocket

You can pipe a message into wssh like netcat to connect, send the message, and disconnect:

	echo "Hello world" | wssh localhost:8000/websocket


