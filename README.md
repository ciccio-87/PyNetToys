# PyNetToys
Experimenting with nonblocking sockets and relays in Python

As of now, it just consists of three scripts (hopefully, they'll be more in future):

 - pync, a (partial) NetCat implementation in Python
 - socks-stub, a very basic (and quite ugly) stub for a 4a socks proxy in Python
 - asocks4a another partial socks4a implementation (client only) with Python asyncore

Please do not expect fantastic performances (socks-stub works with a mixed
threading/select infrastructure) nor total portability (pync uses select on 
stdio descriptors, which is forbidden on Windows).
