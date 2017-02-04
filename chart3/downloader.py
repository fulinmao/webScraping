import random
import urllib2
import urlparse

from chart3.Throttle import Throttle


class Downloader:
    def __init__(self , delay=5 ,user_agent = 'wswp',proxies = None , num_retries = 1 ,cache = None):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.cache = cache

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                # url is not available i
                pass
            else:
                if self.num_retries > 0 and 500 < result['Code'] < 600:
                    # server error so ignore result from cache
                    # and re-download
                    result = None
        if result is None:
            # result was not loaded from cache
            # so still need to download

            self.throttle.wait(url)
            proxy = random.chocie(self.proxies) if self.proxies else None
            headers = {'User-agent':self.user_agent}
            result = self.download(url,headers,proxy=proxy,num_retries=self.num_retries)

            if self.cache :
                # save result to cache
                self.cache[url] = result
        return result['Html']

    def download(self, url, headers, proxy, num_retries, data=None):
        print 'Downloading:', url
        request = urllib2.Request(url, data, headers or {})
        opener = urllib2.build_opener()
        if proxy:
            proxy_params = {urlparse.urlparse(url).scheme: proxy}
            opener.add_handler(urllib2.ProxyHandler(proxy_params))
        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
        except urllib2.URLError as e:
            print 'Download error:', e.reason
            html = ''
            if hasattr(e, 'code'):
                code = e.code
                if num_retries > 0 and 500 <= code < 600:
                    # retry 5XX HTTP errors
                    return self.download(self, url, headers, proxy, num_retries - 1, data)
            else:
                code = None
        return {'Html':html , 'Code':code}