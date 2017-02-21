#!/usr/bin/python

import socket
import sys
import os
import select
import argparse
import subprocess
import shlex


"""
	Ugly and patchy netcat-like python utility
	
	NOTE: won't probably work on Windows (it does not allow to select anything other than sockets)
	TODO:
		- buffering on listen side in UDP but not in TCP, must pick one
		- UDP listen mode always behave like -k, find out why
		- (try to) fix -e functionality for UDP
		- clean up/refactor the *fine* everything (e.g. setblocking not needed for -e, code duplication)
		- maybe more/better comments?
"""

def exec_handle(s, binary):
	p = subprocess.Popen(shlex.split(binary), stdin=s.fileno(), stdout=s.fileno())#, stderr=subprocess.STDOUT)
	p.wait()
	s.close()

def tcp_handle(s):
	while 1:
		try:
			inready, outready, error = select.select([s, sys.stdin],[],[])

			for ir in inready:
				if ir == s:
					res = s.recv(2048)
					if res != '':
						#sys.stdout.write(res)
						os.write(sys.stdout.fileno(), res)
					else:
						s.close()
						return
				else:
					res = os.read(sys.stdin.fileno(), 2048)
					s.sendall(res)
		except (KeyboardInterrupt):
			break

def udp_handle(s, addr=0):
	buf = ''
	while 1:
		try:
			inready, outready, error = select.select([s, sys.stdin],[],[])

			for ir in inready:
				if ir == s:
					res, addr = s.recvfrom(2048)
					if res != '':
						#sys.stdout.write(res)
						os.write(sys.stdout.fileno(),res)
					else:
						s.close()
						return
				else:
					buf += os.read(sys.stdin.fileno(), 2048)
					#print buf
					if addr:
						#print 'now sending to ' + str(addr)
						s.sendto(buf, addr)
						buf = ''
		except (KeyboardInterrupt):
			break


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-l", action='store_true', help='listening mode')
	group.add_argument("destination", type=str, help="destination address", nargs='?')
	parser.add_argument("-p", type=int, help='listening port')
	parser.add_argument("-k", action='store_true', help="Keep inbound socket open")
	parser.add_argument("-u", action='store_true', help="UDP mode")
	parser.add_argument("-e", type=str, help="program to exec after connect [dangerous!!]")
	#parser.add_argument("destination", type=str, help="destination address", nargs='?')
	parser.add_argument("port", type=int, help="destination port", nargs='?')
	args = parser.parse_args()

	#print args

	if args.l and args.p is None:
		parser.print_help()
		print '\n-p option required with -l'
		sys.exit(1)
	elif not args.l and (args.destination is None or args.port is None):
		parser.print_help()
		print '\ndestination and port needed'
		sys.exit(1) 

	if args.u:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	else:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	if args.l:
		try:
			s.bind(('0.0.0.0', args.p))
		except:
			print >>sys.stderr, 'Cannot bind to port'
			sys.exit(1)
		if not args.u:
			s.listen(0)
			try:
				abort = 0
				while not abort:
					c, a = s.accept()
					try:
						c.setblocking(0)
					except:
						pass
					if args.e is None:
						tcp_handle(c)
					else:
						exec_handle(c, args.e)
					if not args.k:
						abort = 1
			except (KeyboardInterrupt):
				s.close()
				sys.exit(0)
		else:
			s.setblocking(0)
			if args.e is None:
				udp_handle(s)
			else:
				exec_handle(s, args.e)
	else:
		if not args.u:
			try:
				s.connect((args.destination, args.port))
			except:
				print >>sys.stderr, 'Cannot connect to destination/port'
				sys.exit(1)
			try:
				s.setblocking(0)
			except:
				pass
			tcp_handle(s)
		else:
			s.setblocking(0)
			udp_handle(s, (args.destination, args.port))