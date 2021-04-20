import urllib.request
from pyquery import PyQuery
import os

BASE_URL = 'https://generalsio-replays-bot.s3.amazonaws.com/'
DESTINATION = '../data'


def main():
    bucket = None
    try:
        bucket = open('../data/bucket.xml', 'r')
        data = bucket.read()
        pq = PyQuery(data, parser='xml')
        keys = [item.text() for item in pq('Key').items()]
        for key in keys:
            url = BASE_URL + key
            urllib.request.urlretrieve(url, filename=os.path.join(DESTINATION,key))
        bucket.close()
    except:
        if not bucket is None:
            bucket.close()


if __name__ == '__main__':
    main()