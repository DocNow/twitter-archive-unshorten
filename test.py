import os
import twitter_archive_unshorten

if os.path.isfile("test-data/data/shorturls.json"):
    os.unlink("test-data/data/shorturls.json")

def test_read_mapping():
    url_map = twitter_archive_unshorten.read_url_map('test-data/data/tweet.js')
    assert len(url_map) == 42

def test_unshorten():
    urls = [
        "https://t.co/7lm4Iajzfq",
        "https://t.co/HPCTGb55xu",
        "https://t.co/4GbE4w5aGf",
        "https://t.co/lefLOqjjoQ",
        "https://t.co/uRauovhYSc",
        "https://t.co/UWQIK31b6D",
        "https://t.co/sE2gYPV8tt",
        "https://t.co/TNgunak1Ws",
        "https://t.co/jlg2M6AZ",
        "https://t.co/ja59OVVkXG",
    ] 

    expected = [
        "https://twitter.com/jameshodges_/status/1256333367458426881/photo/1",
        "https://ift.tt/2KBfneu",
        "https://ift.tt/3uaSCEs",
        "https://twitter.com/scott_bot/status/1158341525518061569/photo/1",
        "https://ift.tt/3eKta2X",
        "https://twitter.com/ElegantGoose/status/899960415148548096",
        "https://twitter.com/thehill/status/969921855430815750",
        "https://m.youtube.com/watch?v=DgGuTicdtyg",
        "https://bit.ly/Po9Kxn",
        "https://twitter.com/laurensx/status/1018301477176119296/photo/1"
    ]

    url_map = twitter_archive_unshorten.unshorten(urls, "test-data")
    for i, short_url in enumerate(urls):
        assert url_map[short_url] == expected[i] 


