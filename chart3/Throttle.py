import urlparse
import datetime
import time

class Throttle:
    '''
    Add a delay between downloads to the same domain
    '''

    def __init__(self,delay):

        # amount of delay between downloads for each domain
        self.delay = delay

        #timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self, url):
        domian = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domian)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds

            if sleep_secs > 0:
                time.sleep(sleep_secs)

        self.domains[domian] = datetime.datetime.now();