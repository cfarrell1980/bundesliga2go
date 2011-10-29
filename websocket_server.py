#!/usr/bin/env python
from gevent_zeromq import zmq
import gevent
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

def app(environ, start_response):
    context = zmq.Context()
    ws = environ['wsgi.websocket']
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    socket.connect('tcp://localhost:3030')
    while True:
      msg = socket.recv()
      ws.send(msg)
      gevent.sleep(0.1)



if __name__ == '__main__':
    print 'here we go...'
    server = WSGIServer(('', 4040), app,
      handler_class=WebSocketHandler)
    server.serve_forever()
