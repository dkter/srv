import argparse
from collections import namedtuple
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape
from twisted.web import server, resource
from twisted.web.static import File, DirectoryLister
from twisted.internet import reactor, endpoints


Category = namedtuple('Category', ['name', 'prefix'])
VID_EXTS = ('.mp4', '.avi', '.mov', '.m4v')
IMG_EXTS = ('.png', '.gif', '.jpeg', '.tif', '.tiff', '.jpg', '.bmp', '.svg')
DOC_EXTS = ('.doc', '.docx', '.pdf', '.txt', '.rtf', '.html', '.epub')
CATEGORIES = (
    Category(name="Folders", prefix="📁"),
    Category(name="Videos", prefix="🎬"),
    Category(name="Images", prefix="🖼"),
    Category(name="Documents", prefix="📄"),
    Category(name="Other", prefix=""),
)


env = Environment(
    loader=PackageLoader('srv', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class DirLister(DirectoryLister):
    def render(self, request):
        dir_template = env.get_template('directory.html')
        request.setHeader('Content-Type', 'text/html; charset=utf-8')

        path = Path(self.path)
        contents = {
            "Folders": [],
            "Videos": [],
            "Images": [],
            "Documents": [],
            "Other": []
        }
        for child in path.iterdir():
            if child.is_dir():
                contents["Folders"].append(child)
            elif child.suffix in VID_EXTS:
                contents["Videos"].append(child)
            elif child.suffix in IMG_EXTS:
                contents["Images"].append(child)
            elif child.suffix in DOC_EXTS:
                contents["Documents"].append(child)
            else:
                contents["Other"].append(child)

        html = dir_template.render(
            path=path,
            contents=contents,
            categories=CATEGORIES,
        )
        return html.encode('utf-8')


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
