# PyNetToys
Experimenting with nonblocking sockets and relays in Python

As of now, it just consists of two scripts (hopefully, they'll be more in future):

 - pync, a (partial) NetCat implementation in Python
 - socks-stub, a very basic (and quite ugly) stub for a 4a socks proxy in Python

Both scripts work with a threading/select mixed infrastructure, so don't expect fantastic
performances nor total portability (e.g. Windows strictly allows select only for sockets).
