#!/usr/bin/env python

"""

usage: twitter-archive-unshorten.py /path/to/your/twitter/archive/directory

Run this program on an unpacked Twitter Archive directory and it will
rewrite the t.co short URLs to their unshortened equivalent.

MAKE A BACKUP TO KEEP THE ORIGINAL TOO!

"""

import re
import os
import sys
import json
import time
import logging
import urllib.error
import urllib.request

from os.path import join

def main():

    # get the twitter archive directory
    if len(sys.argv) != 2:
        sys.exit("usage: unshorten.py <twitter-archive-dir>")
    archive_dir = sys.argv[1]
    sanity_check(archive_dir)

    logging.basicConfig(filename=join(archive_dir, "twitter-archive-unshorten.log"), level=logging.INFO)
    logging.info("rewriting t.co urls with https://github.com/docnow/twitter-archive-unshorten")

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
        text = open(path, encoding="utf8").read()
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
        for line in open(path, encoding="utf8"):
            for short_url in short_urls_in_text(line):
                # remember the mapping only contains https keys
                lookup_url = re.sub(r'^http://', 'https://', short_url)
                if lookup_url in url_map:
                    logging.info("rewriting {short_url} to {long_url} in {path}")
                    line = line.replace(short_url, url_map[lookup_url])
                    rewrote += 1 
                else:
                    print(f"{lookup_url} not found")
            lines.append(line)

        open(path, "w", encoding="utf8").write(''.join(lines))

        if rewrote > 0:
            print(f"rewrote {rewrote} urls in {path}")

def unshorten(urls, archive_dir):
    """Unshorten a list of URLs and return a dictionary of the short/long URLs.
    Also save a copy of the mapping as we go in data/unshorten.json.
    """
    # make the urls unique
    urls = set(urls)

    # where to write the mapping
    url_map_file = join(archive_dir, "data", "shorturls.json")

    # load any existing mapping data (from a previous run perhaps)
    if os.path.isfile(url_map_file):
        url_map = json.load(open(url_map_file, encoding="utf8"))
    else:
        url_map = {}

    # load short/long mapping already present in tweet.js or tweets.js
    tweet_js = join(archive_dir, "data", "tweet.js")
    if not os.path.isfile(tweet_js):
        tweet_js = join(archive_dir, "data", "tweets.js")

    if os.path.isfile(tweet_js):
        url_map.update(read_url_map(tweet_js))

    count = 0
    for short_url in urls:
        count += 1

        # force https: some old t.co URLs use http
        short_url = re.sub(r'^http://', 'https://', short_url)

        # if we already know what the long url is we can skip it
        if short_url in url_map:
            logging.info(f"already have long url for {short_url}")
            continue

        logging.info(f"looking up {short_url}")

        try:
            urllib.request.urlopen(short_url)
        except urllib.error.HTTPError as e:
            if e.code == 301:
                long_url = e.headers.get('Location')
                logging.info(f"got {long_url} for {short_url}")
                # an unescaped " will break JSON serialization
                long_url = long_url.replace('"', '%22')
                url_map[short_url] = long_url

        # print some diagnostics since this could take a while
        msg = f"unshortening urls: {count} / {len(urls)}"
        print('\r' + msg, end='', flush=True)

        # periodically dump the mappings we have
        if archive_dir != "" and len(url_map) % 10 == 0:
            logging.info(f"writing {len(url_map)} urls to {url_map_file}")
            json.dump(url_map, open(url_map_file, "w", encoding="utf8"), indent=2)

        # try not to awaken the dragon
        time.sleep(.5)

    print()
    return url_map

def read_url_map(path):
    """Read short/long mapping in existing data.
    """
    text = open(path, encoding="utf8").read()
    text = re.sub(r'^window.YTD.tweets?.part0 = ', '', text)
    data = json.loads(text)
    url_map = {}
    for tweet in data:
        entities = tweet['tweet']['entities']['urls']
        entities.extend(tweet['tweet']['entities'].get('media', []))
        for url in tweet['tweet']['entities']['urls']:
            short_url = re.sub(r'^http://', 'https://', url['url'])
            if short_url.startswith('https://t.co/'):
                url_map[short_url] = url['expanded_url']
            
    return url_map

# Some shenanigans so urllib gets the redirect but doesn't follow it.
# It would be nice to be able to use requests here but I didn't want to
# make people install anything extra.
#
# It might be worth revisiting this since it is pip installed now.

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_):
        return None

opener = urllib.request.build_opener(NoRedirect)
urllib.request.install_opener(opener)

if __name__ == "__main__":
    main()
