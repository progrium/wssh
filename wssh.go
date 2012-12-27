package main

import (
	"flag"
	"io"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"strings"

	"code.google.com/p/go.net/websocket"
)

var ignoreEof *bool = flag.Bool("i", false, "Ignore EOF on STDIN")
var listenMode *bool = flag.Bool("l", false, "Listen mode (run a server)")

func attach(ws *websocket.Conn) chan error {
	err := make(chan error, 2)
	go func() {
		_, e := io.Copy(os.Stdout, ws)
		err <- e
	}()
	go func() {
		_, e := io.Copy(ws, os.Stdin)
		if !*ignoreEof {
			err <- e
		}
	}()
	return err
}

func connect(url *url.URL) {
	origin := "http://localhost/"
	ws, err := websocket.Dial(url.String(), "", origin)
	defer ws.Close()
	if err != nil {
		log.Fatalf("connect: %v", err)
	}
	<-attach(ws)
}

func listen(url *url.URL) {
	l, err := net.Listen("tcp", url.Host)
	if err != nil {
		log.Fatalf("listen: %v", err)
	} else {
		http.Serve(l, websocket.Handler(func(ws *websocket.Conn) {
			defer l.Close()
			<-attach(ws)
		}))
	}
}

func main() {
	flag.Parse()

	arg := flag.Arg(0)
	if !strings.Contains(arg, "://") {
		arg = "ws://" + arg
	}
	url, err := url.Parse(arg)
	if err != nil {
		log.Fatal(err)
	}

	if *listenMode {
		listen(url)
	} else {
		connect(url)
	}

}
