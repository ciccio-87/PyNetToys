#!/usr/bin/python

import asyncore
import socket
import struct

def parse_socks(r):
	if not r.startswith('\x04\x01'):
		print "Unsupported command, closing"
		reply = '\x00\x5b'
		return reply, None

	port = socket.ntohs(struct.unpack('<H',r[2:4])[0])
	if r[4:8].startswith('\x00\x00\x00'):
		user, host = r[8:].split('\x00')[:-1]
	else:
		host = socket.inet_ntoa(r[4:8])
		user = r[8:]
	
	if not len(user):
		user = 'Anonymous'

	s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s2.connect((host,port))
	except:
		reply = '\x00\x5b' + r[2:4] + r[4:8]
		s2.close()
		return reply, None
	s2.setblocking(0)
	reply = '\x00\x5a' + r[2:4] + r[4:8]
	return reply, s2



class Relay(asyncore.dispatcher_with_send):
	def __init__(self, sockin, relayback=None):
		asyncore.dispatcher_with_send.__init__(self, sockin)
		#self.sockout = sockout
		self.relayback = relayback

	def handle_read(self):
		data = self.recv(4096)
		if data:
			if self.relayback is None:
				reply, s = parse_socks(data)
				if s is not None:
					self.relayback = Relay(s, self)
					self.send(reply)
				else:
					self.send(reply)
					self.close()
			else:
				self.relayback.send(data)

class Listener(asyncore.dispatcher_with_send):

    def __init__(self, listener_addr):
        asyncore.dispatcher_with_send.__init__(self)
       	self.server = None
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(listener_addr)
        self.listen(5)
        #self.relays = []

    def handle_accept(self):
        conn, addr = self.accept()
        #self.relays.append(Relay(conn))
        rel = Relay(conn)

if __name__ == '__main__':
	socks = Listener(('0.0.0.0', 9000))
	asyncore.loop()