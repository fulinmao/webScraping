import robotparser
import urlparse

import re

from chart3.downloader import Downloader


def link_crawler(seed_url , link_regex = None , delay = 5 , max_depth = -1 , max_urls = -1 ,
                 user_agent = 'wswp' ,proxies = None , num_retries = 1 , scrape_callback=None,cache=None):
    '''Crawl from the given seed URL following links matched by link_regex
    '''

    # the queue of URL's that still need to be crawle
    crawl_queue = [seed_url]

    #the URL's that have been seen and at what depth
    seen = {seed_url :0}

    #trace how many URL's have been downloaded
    num_urls = 0

    rp = get_robots(seed_url)
    D = Downloader(delay=delay , user_agent= user_agent, proxies=proxies,
                   num_retries = num_retries , cache = cache)
    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]

        #check url passes robots.txt restrictions
        if rp.can_fetch(user_agent , url):
            html = D(url)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url,html) or [])

            if depth != max_depth:
                # can still crawl further

                if link_regex:
                    links.extend(link for link in get_links(html)
                        if re.match(link_regex , link) )
                for link in links:
                    link = normalize(seed_url , link)

                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1

                        if same_domain(seed_url,link):
                            crawl_queue.append(link)
            num_urls += 1
            if num_urls == max_urls:
                break;

        else:
            print 'Blocked by robots.txt:', url



def normalize(seed_url,link):
    """
    Normalize this URL by removing hash and adding domain
    :param seed_url:
    :param link:
    :return:
    """
    link, _ = urlparse.urldefrag(link)
    return urlparse.urljoin(seed_url,link)

def same_domain(url1,url2):
    """
    Return true if both URL's belong to same domain
    :param url1:
    :param url2:
    :return:
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc

def get_robots(url):
    """ Initialize robts parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url,'/robots.txt'))
    rp.read()
    return rp

def get_links(html):
    """
    Return ja list of links from html
    :param html: from html
    :return:
    """
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']',re.IGNORECASE)
    return webpage_regex.findall(html)

if __name__ == '__main__':
    # link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, max_depth=1,
                 user_agent='GoodCrawler')


