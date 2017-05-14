# SimpleHTTPServer but with range requests

from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor

import sys

PORT = 8000 if len(sys.argv) < 2 else int(sys.argv[1])

f = File('.')
s = Site(f)
reactor.listenTCP(PORT, s, interface='0.0.0.0')
reactor.run()
