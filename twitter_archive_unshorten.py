#!/usr/bin/env python

"""

usage: unshorten.py /path/to/your/twitter/archive/directory

Run this program on an unpacked Twitter Archive directory and it will
rewrite the t.co short URLs to their unshortened equivalent.

MAKE A BACKUP TO KEEP THE ORIGINAL TOO!

"""

import re
import os
import sys
import json
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

    # find all the short urls in the archive
    short_urls = get_short_urls(archive_dir)

    # unshorten them
    url_map = unshorten(short_urls, archive_dir)

    # rewrite the files using the short url mapping
    rewrite_files(archive_dir, url_map)

def sanity_check(archive_dir):
    if not os.path.isfile(join(archive_dir, 'Your archive.html')) or \
            not os.path.isdir(join(archive_dir, 'assets')) or \
            not os.path.isdir(join(archive_dir, 'data')):
        sys.exit("🆘 {archive_dir} isn't a Twitter archive directory!")

    print("The t.co URLs in your Twitter archive data will be overwritten.")
    print()
    answer = input("Do you have a backup? Y/N ")
    if answer.upper() != "Y":
        sys.exit("🆘 please go make a backup first!")


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
    # It's important to sort these since not all t.co URLs are 23 characters long and
    # the length matters when we are replacing. We don't want to accidentally
    # overwrite part of another URL with a shorter one. If they are done in
    # order of their length that won't happen.
    urls = re.findall(r'https?://t.co/[a-zA-Z0-9…]+', s)
    urls = filter(lambda url: not url.endswith('…'), urls)
    return sorted(urls, key=len, reverse=True)

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

        # rewriting line by line is more efficent
        lines = []
        rewrote = 0
        for line in open(path):
            for short_url in short_urls_in_text(line):
                # remember the mapping only contains https keys
                lookup_url = re.sub(r'^http://', 'https://', short_url)
                if lookup_url in url_map:
                    rewrote += 1 
                    line = line.replace(short_url, url_map[lookup_url])
                else:
                    print(f"{lookup_url} not found")
            lines.append(line)

        open(path, "w").write(''.join(lines))

        if rewrote > 0:
            print(f"rewrote {rewrote} urls in {path}")

def unshorten(urls, archive_dir):
    """Unshorten a list of URLs and return a dictionary of the short/long URLs.
    Also save a copy of the mapping as we go in data/unshorten.json.
    """
    # make the urls unique
    urls = set(urls)

    # where to write the mapping
    url_map_file = join(archive_dir, "data", "urlmap.json")

    # load any mapping data we have already
    if os.path.isfile(url_map_file):
        url_map = json.load(open(url_map_file))
    else:
        url_map = {}

    count = 0
    for short_url in urls:
        count += 1

        # force https: some old t.co URLs use http
        short_url = re.sub(r'^http://', 'https://', short_url)
        try:
            urllib.request.urlopen(short_url)
        except urllib.error.HTTPError as e:
            if e.code == 301:
                long_url = e.headers.get('Location')
                # an unescaped " will break JSON serialization
                long_url = long_url.replace('"', '%22')
                url_map[short_url] = long_url

        # print some diagnostics since this could take a while
        msg = f"unshortening urls: {count} / {len(urls)}"
        print('\r' + msg, end='', flush=True)

        # periodically dump the mappings we have
        if len(url_map) % 10 == 0:
            json.dump(url_map, open(url_map_file, "w"), indent=2)

        # try not to awaken the dragon
        time.sleep(.5)

    print()
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
