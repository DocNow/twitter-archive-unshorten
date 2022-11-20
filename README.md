# twitter-archive-unshorten (still in development)

Twitter's [archive download](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive) includes shortened `t.co` URLs instead of the original URLs that you tweeted. This is kind of a problem if Twitter ever goes away, because the server at `t.co` won't be available to respond to requests. Somewhat oddly the archive download itself contains some of these expanded URLs but not in a uniform way, and the user interface doesn't seem to use them.

`unshorten.py` is a small Python program that will examine all the JavaScript files in the archive download and rewwrite all the `t.co` short URLs back into their original full URL form. This means the context for your archived tweets will make a little more sense after Twitter is gone. Maybe you can look up those URLs in the Internet Archive if they are no longer available. This would be impossible if all you had was the short URL.

## Run

1. Unzip your Twitter archive zip file.
2. Download [unshorten.py](https://raw.githubusercontent.com/DocNow/twitter-archive-unshorten/main/unshorten.py).
3. Open a terminal window and run: `python3 unshorten.py /path/to/your/archive`

It might take a while, depending on how many tweets you have. Once it's
finished you should be able open your Archive and interact with it without the
`t.co` URLs.
