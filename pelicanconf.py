#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Sam Frances'
SITENAME = u"Sam Frances' Blog"
SITEURL = ''

PATH = 'content'
OUTPUT_PATH = 'output/'

TIMEZONE = 'Europe/London'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('Xophmeister\'s World', 'http://xoph.co/'),)

# Social widget
SOCIAL = (('stackoverflow', 'http://stackoverflow.com/users/1256529/samfrances'),
          ('github', 'http://github.com/samfrances'),
          ('codewars', 'http://codewars.com/users/samfrances'),)

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# User added from now on

#THEME = 'themes/pelican-blueidea'
THEME = 'themes/samfrances-theme'

# URL setiings
ARTICLE_URL = 'posts/{date:%Y}/{date:%b}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%b}/{date:%d}/{slug}/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
CATEGORY_URL = '{slug}/'
CATEGORY_SAVE_AS = '{slug}/index.html'
AUTHOR_SAVE_AS = '' # Author page not needed, only one author
INDEX_SAVE_AS = 'all/index.html'

