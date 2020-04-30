from twisted.web import server, resource
from twisted.web.static import File
from twisted.internet import reactor, endpoints

import argparse


parser = argparse.ArgumentParser()
parser.add_argument('dir', help="the directory to serve")
parser.add_argument('-p', '--port', type=int, default=8000,
                    help="the port to listen on")
args = parser.parse_args()

resource = File(args.dir)
factory = server.Site(resource)
endpoint = endpoints.TCP4ServerEndpoint(reactor, args.port)
endpoint.listen(factory)
reactor.run()
