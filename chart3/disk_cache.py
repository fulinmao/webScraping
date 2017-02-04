import os
import urlparse
import re

import pickle

import zlib

from datetime import timedelta , datetime

from chart3.link_crawler import link_crawler


class DiskCache:
    def __init__(self , cache_dir = "cache",max_length = 255, expires=timedelta(days=30) ):
        self.cache_dir = cache_dir
        self.max_length = max_length
        self.expires = expires

    def url_to_path(self, url):
        """
        Create file System path for URL
        :param url:
        :return:
        """
        components = urlparse.urlsplit(url)
        # append index.html to empty paths

        path = components.path
        if not path:
            path = 'index.html'
        elif path.endswith('/'):
            path += 'index.html'

        filename = components.netloc + path + components.query

        # replace invalid characters
        filename = re.sub('[^/0-9a-zA-Z\-.,;_ ]','_' , filename)

        # restrict maximum number of characters
        filename = '/'.join( segment[:self.max_length] for segment in filename.split('/'))

        return os.path.join(self.cache_dir,filename)


    def __getitem__(self, url):
        """
        load data from disk for this URL
        :param url:
        :return:
        """
        path = self.url_to_path(url)

        if os.path.exists(path):
            with open(path, 'rb') as fp:
                data = fp.read()
                data = zlib.decompress(data)
                result, timestamp = pickle.loads(data)
                if self.has_expired(timestamp):
                    raise KeyError(url + ' has expired')
                return result
        else:
            # URL has not yet been cached
            raise KeyError(url + 'does not exist')

    def __setitem__(self, url, result):
        """
        Save data to disk for this url
        :param url:
        :param result:
        :return:
        """
        path = self.url_to_path(url)
        folder = os.path.dirname(path)

        if not os.path.exists(folder):
            os.makedirs(folder)

        data = pickle.dumps((result, datetime.utcnow()))
        data = zlib.compress(data)
        with open(path, 'wb') as fp:
            fp.write(data)

    def has_expired(self,timestamp):
        """
        Return whether this timestamp has expired
        :param timestamp:
        :return:
        """
        return datetime.utcnow() > timestamp + self.expires;
if __name__ =='__main__':
    timestamp = datetime.utcnow();
    link_crawler('http://example.webscraping.com/', '/(index|view)', cache=DiskCache())
    print datetime.utcnow() - timestamp