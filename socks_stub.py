#!/usr/bin/python

import socket
import threading
import select
import struct
import time


"""

An ugly stub for a 4a forward socks proxy.

No authentication supported (if a username is supplied, it's logged then happily ignored).
Quite sure not so good performances (python + threads/select mixed infrastructure).
Reverse (listen) proxy should be easy to add, but I'm not even sure I understood how it should work.
Code is pretty horrible indeed.

"""


printlock = threading.Lock()
stop = False

def relay_handle(s1, s2):
	sockets = [s1, s2]
	fail = False
	try:
		s1.setblocking(0)
		s2.setblocking(0)
	except:
		pass
	while not stop:
		try:
			inready, outready, error = select.select([s1,s2],[],[], 5)
			for ir in inready:
				res = ir.recv(2048)
				if res != '':
					if ir == s1:
						s2.sendall(res)
					else:
						s1.sendall(res)
				else:
					#break
					s1.close()
					s2.close()
					return
		except:
			fail = True
			break

	s1.close()
	s2.close()
	return fail

def handle4a(tid,s,client):
	r = s.recv(2048) # MAX_HOSTNAME should be 255, if it doesn't fit here, something must be fucked up
	#print r.encode('hex')
	if not r.startswith('\x04\x01'):
		with printlock:
			print "[Thread %i] Unsupported command" % tid
		s.send('\x00\x5b')
		s.close()
		return
	port = socket.ntohs(struct.unpack('<H',r[2:4])[0])
	if r[4:8].startswith('\x00\x00\x00'):
		user, host = r[8:].split('\x00')[:-1]
	else:
		host = socket.inet_ntoa(r[4:8])
		user = r[8:]
	
	if not len(user):
		user = 'Anonymous'

	with printlock:
		print "[Thread %i] Trying to connect user %s, at %s to host %s, port %i" % (tid, user, client, host, port)
	
	s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s2.connect((host,port))
	except:
		with printlock:
			print "[Thread %i] Can't connect to remote host" % tid
		s.send('\x00\x5b' + r[2:4] + r[4:8])
		s.close()
		s2.close()
		return
	s.send('\x00\x5a' + r[2:4] + r[4:8])
	with printlock:
		print "[Thread %i] Start relaying from %s to %s:%i" % (tid, client, host, port)
	
	fail = relay_handle(s,s2)
	with printlock:
		if fail:
			print  "[Thread %i] Failure" % tid
		else:
			print "[Thread %i] Exiting" % tid



if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	threads = []
	i = 0
	s.bind(('0.0.0.0', 9000))
	s.listen(0)
	while 1:
		try:

			c,a = s.accept()
			print a
			time.sleep(.3)
			t = threading.Thread(target=handle4a, args=(i,c,a))
			i += 1
			threads.append(t)
			t.start()

		except (KeyboardInterrupt):
				break
	stop = True
	s.close()
	with printlock:
		print "Waiting for threads to stop"
	for th in threads:
		th.join()

