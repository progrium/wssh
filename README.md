# wssh - websocket shell

wssh ("wish") is a command-line utility/shell for WebSocket inpsired by netcat.

## Install

	git clone git://github.com/progrium/wssh.git
	cd wssh
	python setup.py install

## Usage

Listen for WebSocket connections on a particular path and print messages to STDOUT:

	wssh -l localhost:8000/websocket

Once connected you can use STDIN to send messages. Each line is a message. You can just as well open a peristent client connection that prints incoming messages to STDOUT and sends messages from STDIN interactively:

	wssh localhost:8000/websocket

