#!/usr/bin/env python

"""

Run this program in the an unpacked Twitter Archive directory and it will
rewrite the t.co short URLs to their unshortened equivalent.

*** MAKE A BACKUP TO KEEP THE ORIGINAL TOO! ***

"""

import re
import os
import sys
import time
import urllib.error
import urllib.request

from os.path import join

def main():

    # get the twitter archive directory
    if len(sys.argv) != 2:
        sys.exit("usage: unshorten.py <twitter-archive-dir>")

    archive_dir = sys.argv[1]
    sanity_check(archive_dir)

    short_urls = get_short_urls(archive_dir)

    url_map = unshorten(short_urls)

    rewrite_files(archive_dir, url_map)

def sanity_check(archive_dir):
    if not os.path.isfile(join(archive_dir, 'Your archive.html')) or \
            not os.path.isdir(join(archive_dir, 'assets')) or \
            not os.path.isdir(join(archive_dir, 'data')):
        sys.exit("You aren't running from a Twitter archive directory!")

def get_short_urls(archive_dir):
    """
    Gets all the t.co URLs in the archive.
    """
    urls = []
    for path in get_js_files(archive_dir):
        text = open(path).read()
        urls.extend(short_urls_in_text(text))
    return urls

def short_urls_in_text(s):
    """Get the t.co URLs in a string.
    """
    return re.findall(r'https://t.co/[a-zA-Z0-9]+', s)

def get_js_files(archive_dir):
    """Get the files in the archive that need to be rewritten.
    """
    for root_dir, _, files in os.walk(archive_dir):
        for filename in files:
            ext = os.path.splitext(filename)[1]
            if ext == ".js":
                yield(os.path.join(root_dir, filename))

def rewrite_files(archive_dir, url_map):
    """Rewrite all the .js archive files using the URL mapping.
    """
    for path in get_js_files(archive_dir):
        text = open(path).read()
        for short_url in short_urls_in_text(text):
            if short_url in url_map:
                text = text.replace(short_url, url_map[short_url])
        print("rewriting %s" % path)
        open(path, "w").write(text)

def unshorten(urls):
    """Unshorten a list of URLs and return a dictionary of the short/long URLs.
    """
    # make the urls unique
    urls = set(urls)

    url_map = {}
    for short_url in urls:
        try:
            urllib.request.urlopen(short_url)
        except urllib.error.HTTPError as e:
            if e.code == 301:
                long_url = e.headers.get('Location')
                url_map[short_url] = long_url

        # print some diagnostics, gonna take a while potentially
        msg = 'unshortening urls: %s / %s' % (len(url_map), len(urls))
        print('\r' + msg, end='', flush=True)

        # try not to awaken the beast
        time.sleep(.5)

    return url_map

# Some shenanigans so urllib gets the redirect but doesn't follow it.
# It would be nice to be able to use requests here but I didn't want to
# make people install anything extra.

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_):
        return None

opener = urllib.request.build_opener(NoRedirect)
urllib.request.install_opener(opener)

if __name__ == "__main__":
    main()
