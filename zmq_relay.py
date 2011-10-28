#!/usr/bin/env python
import zmq
from time import sleep

context = zmq.Context()
sub = context.socket(zmq.REP)
pub = context.socket(zmq.PUB)

sub.bind("tcp://*:6060")
pub.bind("tcp://*:3030")
while (True):
  msg = sub.recv()
  sub.send("%s - thanks"%msg)
  pub.send(msg)
  sleep(0.3)
