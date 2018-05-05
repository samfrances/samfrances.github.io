from fabric.api import *
import os
import shutil
import sys
import SocketServer
from datetime import datetime  # User addition
from uuid import uuid4

from pelican.server import ComplexHTTPRequestHandler

import pelicanconf

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'
DEPLOY_PATH = env.deploy_path

# Port for `serve`
PORT = 8000


def clean():
    """Remove generated files"""
    if os.path.isdir(DEPLOY_PATH):
        shutil.rmtree(DEPLOY_PATH)
        os.makedirs(DEPLOY_PATH)


def build(publish=False):
    """Build local version of site"""
    if publish:
        local('pelican -s publishconf.py')
    else:
        local('pelican -s pelicanconf.py')

    # Copy CNAME file (for Github Pages)
    local('cp CNAME {}/'.format(DEPLOY_PATH))

    # Make blog category page the index
    output_path = pelicanconf.OUTPUT_PATH.strip("/")
    blog_index = pelicanconf.CATEGORY_SAVE_AS.strip("/")

    local('cp {output_path}/{blog_index} {output_path}/index.html'.format(
        output_path=output_path,
        blog_index=blog_index.format(slug="blog"),
    ))


def rebuild(publish=False):
    """`clean` then `build`"""
    clean()
    build(publish=publish)


def serve():
    """Serve site at http://localhost:8000/"""
    os.chdir(env.deploy_path)

    class AddressReuseTCPServer(SocketServer.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(('', PORT), ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {0} ...\n'.format(PORT))
    server.serve_forever()


def reserve():
    """`build`, then `serve`"""
    build()
    serve()


# Extra utility functions

TEMPLATE = """
Title: {title}
Date: {year}-{month}-{day} {hour}:{minute:02d}
UniqueId: {year}-{month}-{day}-{slug}-{uuid}
Modified:
Category:
Tags:
Slug: {slug}
Authors:
Summary:
Status:draft



"""


def make_entry(title):
    today = datetime.today()
    slug = title.lower().strip().replace(' ', '-')
    f_create = "content/{}_{:0>2}_{:0>2}_{}.md".format(
        today.year, today.month, today.day, slug)
    t = TEMPLATE.strip().format(title=title,
                                year=today.year,
                                month=today.month,
                                day=today.day,
                                hour=today.hour,
                                minute=today.minute,
                                slug=slug,
                                uuid=uuid4())
    with open(f_create, 'w') as w:
        w.write(t)
    print("File created -> " + f_create)
