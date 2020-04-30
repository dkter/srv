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

FOLDERS = Category(name="Folders", prefix="📁")
VIDEOS = Category(name="Videos", prefix="🎬")
IMAGES = Category(name="Images", prefix="🖼")
DOCUMENTS = Category(name="Documents", prefix="📄")
OTHER = Category(name="Other", prefix="")
CATEGORIES = (FOLDERS, VIDEOS, IMAGES, DOCUMENTS, OTHER)


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
            FOLDERS: [],
            VIDEOS: [],
            IMAGES: [],
            DOCUMENTS: [],
            OTHER: []
        }
        for child in path.iterdir():
            if child.is_dir():
                contents[FOLDERS].append(child)
            elif child.suffix in VID_EXTS:
                contents[VIDEOS].append(child)
            elif child.suffix in IMG_EXTS:
                contents[IMAGES].append(child)
            elif child.suffix in DOC_EXTS:
                contents[DOCUMENTS].append(child)
            else:
                contents[OTHER].append(child)

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
