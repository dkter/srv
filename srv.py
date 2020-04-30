import argparse

from twisted.web import server, resource
from twisted.web.static import File, DirectoryLister
from twisted.internet import reactor, endpoints


class DirLister(DirectoryLister):
    def render(self, request):
        request.setHeader('Content-Type', 'text/html')
        return b"<h1>Hello, world!</h1>"


class DirPage(File):
    def directoryListing(self):
        return DirLister(self.path,
                         self.listNames(),
                         self.contentTypes,
                         self.contentEncodings,
                         self.defaultType)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help="the directory to serve")
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help="the port to listen on")
    args = parser.parse_args()

    resource = DirPage(args.dir)
    factory = server.Site(resource)
    endpoint = endpoints.TCP4ServerEndpoint(reactor, args.port)
    endpoint.listen(factory)
    reactor.run()
