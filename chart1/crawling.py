import urllib2
import re
import itertools
import urlparse
import robotparser


def download(url):
    return urllib2.urlopen(url).read()

def downloadUserAgent(url,user_agent='wswp',proxy=None,num_retried = 2):
    print 'Downloading:' , url
    headers = {'User_agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    opener = urllib2.build_opener()

    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme:proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))

    try:
        html = opener.open(request).read()
        #html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error :',e.reason
        if num_retried > 0 :
            if hasattr(e , 'code') and 500 <= e.code <= 600 :
                return download(url,user_agent, num_retried - 1)
        html = None
    return html

def download(url,num_retried = 2):
    print 'Downloading:' , url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error :',e.reason
        if num_retried > 0 :
            if hasattr(e , 'code') and 500 <= e.code <= 600 :
                return download(url, num_retried - 1)
        html = None
    return html

def crawl_sitemap(url):
    #download the sitemap file
    sitemap = download(url)
    #extract the sitemap links
    links = re.findall('<loc>(.*?)</loc>',sitemap)
    # download each link
    for link in links :
        print link
        # html = download(link)

def crawl_id(url,max_errors=5):
    num_errors = 0
    for page in itertools.count(1):
        crawl_url = url % page
        html = download(crawl_url)
        if html is None:
            num_errors += 1;
            if num_errors == max_errors:
                break
            break
        else:
            pass

def link_crawler(seed_url,link_regex,max_depth = 2 ):
    '''
    crawl from the given seed url following links matched by link_regex
    :param seed_url:
    :param link_regex:
    :return:
    '''
    crawl_queue = [seed_url]
    #crawled_set = set(seed_url)
    crawled = {}

    while crawl_queue:
        url = crawl_queue.pop();
        depth = crawled[seed_url]
        if can_fetch(user_agent='' , url = url):
            html = downloadUserAgent(url)
        else:
            print 'Blocked by robot.txt :' , url
        # filter for links matching our regular expression
        if depth  != max_depth:
            for link in get_links(html):
                if re.match(link_regex,link):
                    link = urlparse.urljoin(seed_url,link)
                    # check if have already seen this link
                    if link not in crawled:
                        crawled[link] = depth + 1;
                        crawl_queue.append(link)

def get_links(html):
    '''
    Return a list of links from html
    :param html:
    :return:
    '''

    # a regular expression to extract all links from webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']' , re.IGNORECASE)

    # list of all links from webpage
    return webpage_regex.findall(html)

def can_fetch(user_agent , url):
    '''check robot.txt'''
    rp = robotparser.RobotFileParser();
    rp.set_url('http://example.webscraping.com/robots.txt')
    rp.read()
    return rp.can_fetch(user_agent,url)

if __name__ == '__main__':
    # url = "http://www.meetup.com"
    # print download(url)
    # url = "http://example.webscraping.com/view/-%d"
    # crawl_id(url)
    seed_url = "http://example.webscraping.com/"
    link_regex = "/(index|view)"
    link_crawler(seed_url,link_regex)
