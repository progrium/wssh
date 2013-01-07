# wssh - websocket shell

wssh ("wish") is a command-line utility/shell for WebSocket inpsired by netcat.

## Install

- Assumes Python 2.7

It uses currently uses gevent 0.13, so you may need to install libevent. This is because it uses the great work in [ws4py](https://github.com/Lawouach/WebSocket-for-Python). My gevent websocket server+client in there could probably be generalized to work with Eventlet; then this could be trivially ported to Eventlet to drop the libevent dependency.

If you don't have libevent installed already, install it prior to running setup.py. You can install libevent using `apt-get` on Ubuntu or `brew` on a Mac. 

	git clone git://github.com/progrium/wssh.git
	cd wssh
	python setup.py install

## Usage

Listen for WebSocket connections on a particular path and print messages to STDOUT:

	wssh -l localhost:8000/websocket

Once connected you can use STDIN to send messages. Each line is a message. You can just as well open a peristent client connection that prints incoming messages to STDOUT and sends messages from STDIN interactively:

	wssh localhost:8000/websocket

## Contributing

Feel free to fork and improve.

## License 

MIT
