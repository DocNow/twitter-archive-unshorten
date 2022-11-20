# twitter-archive-unshorten

Twitter's [archive download](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive) includes shortened `t.co` URLs instead of the original URLs that you tweeted. If Twitter ever goes away, the server at `t.co` won't be available to respond to requests.

`twitter-archive-unshorten` is a small Python program that will examine all the JavaScript files in the archive download and rewrite the `t.co` short URLs to their original full URL form. This means the context for your archived tweets will make a little more sense after Twitter is gone. Maybe you can look up those URLs in the Internet Archive if they are no longer available. This would be impossible if all you had was the short URL.

## Install

```
$ pip3 install twitter-archive-unshorten
```

## Run

1. Unzip your Twitter archive zip file.
3. Open a terminal window and run: `twitter-archive-unshorten /path/to/your/archive/directory/`

It might take a while, depending on how many tweets you have. Once it's
finished you should be able open your Archive and interact with it without the
`t.co` URLs.

The mapping of short URLs to long URLs that was used is saved in your archive directory as
`data/shorturls.json`.
