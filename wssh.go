package main

import (
  "flag"
	"fmt"
	"io"
  "os"
  "net"
	"net/http"
	"code.google.com/p/go.net/websocket"
)

var port *int = flag.Int("p", 23456, "Port to listen/connect on")
var ignoreEof *bool = flag.Bool("i", false, "Ignore EOF on STDIN")
var listenMode *bool = flag.Bool("l", false, "Listen mode (run a server)")

func attach(ws *websocket.Conn) chan bool {
  eof := make(chan bool, 1)
  go func() {
    io.Copy(os.Stdout, ws)
    eof <- true
  }()
  go func() {
    io.Copy(ws, os.Stdin)
    if !*ignoreEof {
      eof <- true
    }
  }()
  return eof
}


func connect() {
  origin := "http://localhost/"
  url := fmt.Sprintf("ws://localhost:%d/", *port)
  ws, err := websocket.Dial(url, "", origin)
  defer ws.Close()
  if err != nil {
    panic("connect: " + err.Error())
  }
  <-attach(ws)
}

func listen() {
  l, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
  if err != nil {
    panic("listen: " + err.Error())
  } else {
    http.Serve(l, websocket.Handler(func(ws *websocket.Conn) {
      defer l.Close()
      <-attach(ws)
    }))
  }
}

func main() {
  flag.Parse()
  fmt.Printf("http://localhost:%d/\n", *port)

  if *listenMode {
    listen()
  } else {
    connect()
  }

}
