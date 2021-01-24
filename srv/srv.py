"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

This Source Code Form is "Incompatible With Secondary Licenses", as
defined by the Mozilla Public License, v. 2.0.
"""

import argparse
import socket
import sys
from collections import namedtuple
from pathlib import Path
from typing import Dict, List, Callable

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


def format_size(nbytes: float) -> str:
    suffixes = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB")
    suffix = 0
    while suffix < len(suffixes) - 1 and nbytes >= 1024:
        nbytes /= 1024
        suffix += 1
    return f"{nbytes:.3g} {suffixes[suffix]}"


class DirLister(DirectoryLister):
    def render(self, request) -> bytes:
        request.setHeader('Content-Type', 'text/html; charset=utf-8')
        dir_template = env.get_template('directory.html')

        path = Path(self.path)
        contents: Dict[Category, List[Path]] = {
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
            format_size=format_size,
        )
        return html.encode('utf-8')


class DirPage(File):
    def directoryListing(self) -> DirectoryLister:
        return DirLister(self.path,
                         self.listNames(),
                         self.contentTypes,
                         self.contentEncodings,
                         self.defaultType)


class TextPage(resource.Resource):
    isLeaf = True

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def render_GET(self, request) -> bytes:
        request.setHeader(b"Content-Type", b"text/plain")
        return self.text.encode("utf-8")


def printStatus(dir: str, port: int) -> Callable[[int], None]:
    def onIP(ip: int):
        if dir is not None:
            print(f"Serving {dir} on {ip}:{port}")
        else:
            print(f"Serving on {ip}:{port}")
    return onIP


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs='?', default='.',
                        help="the directory to serve")
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help="the port to listen on")
    parser.add_argument('-r', '--raw', type=str, nargs='?', const=None, default=argparse.SUPPRESS,
                        help="the port to listen on")
    args = parser.parse_args()

    if 'raw' not in args:
        resource = DirPage(args.dir)
        dir = args.dir
    else:
        if args.raw is None:
            args.raw = sys.stdin.read()
        resource = TextPage(args.raw)
        dir = None
    factory = server.Site(resource)
    endpoint = endpoints.TCP4ServerEndpoint(reactor, args.port)

    endpoint.listen(factory)
    reactor.resolve(socket.getfqdn()).addCallback(printStatus(dir, args.port))
    reactor.run()


if __name__ == '__main__':
    main()
