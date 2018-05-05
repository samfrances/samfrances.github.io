from fabric.api import *
import fabric.contrib.project as project
import os
import shutil
import sys
import SocketServer
from datetime import datetime # User addition
import confidential # User addition
from uuid import uuid4

from pelican.server import ComplexHTTPRequestHandler

import pelicanconf

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'
DEPLOY_PATH = env.deploy_path

# Remote server configuration
production = confidential.production
dest_path = confidential.dest_path

# Rackspace Cloud Files configuration settings
env.cloudfiles_username = 'my_rackspace_username'
env.cloudfiles_api_key = 'my_rackspace_api_key'
env.cloudfiles_container = 'my_cloudfiles_container'

# Github Pages configuration
env.github_pages_branch = "gh-pages"

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

#def regenerate():
#    """Automatically regenerate site upon file modification"""
#    local('pelican -r -s pelicanconf.py')

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

#def preview():
#    """Build production version of site"""
#    local('pelican -s publishconf.py')

#def cf_upload():
#    """Publish to Rackspace Cloud Files"""
#    rebuild()
#    with lcd(DEPLOY_PATH):
#        local('swift -v -A https://auth.api.rackspacecloud.com/v1.0 '
#              '-U {cloudfiles_username} '
#              '-K {cloudfiles_api_key} '
#              'upload -c {cloudfiles_container} .'.format(**env))

@hosts(production)
def publish():
    """Publish to production via rsync"""
    rebuild(publish=True)
    project.rsync_project(
        remote_dir=dest_path,
        exclude=".DS_Store",
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True,
        extra_opts='-c',
    )

#def gh_pages():
#    """Publish to GitHub Pages"""
#    rebuild()
#    local("ghp-import -b {github_pages_branch} {deploy_path}".format(**env))
#    local("git push origin {github_pages_branch}".format(**env))


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


