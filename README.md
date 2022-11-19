# twitter-archive-unshorten

Twitter's [archive download](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive) includes shortened URLs instead of the original. This is kind of a problem if Twitter ever goes away.

`unshorten.py` is a small Python3 program for converting all the `t.co` short URLs in your Twitter archive download back to the original full URL. That way you can see what you were originally referring to when Twitter is no more.

## Run

1. Unzip your archive.
2. Download and move `unshorten.py` into the archive directory that was created.
3. Open a terminal window `python3 unshorten.py /path/to/your/archive`

Once it's finished you should be able open your Archive and interact with it without the `t.co` URLs.
