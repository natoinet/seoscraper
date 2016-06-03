from collections import deque

from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner

from seoscraper.spiders.seoscraper_spider import SeoScraperSpider
from seoscraper.spiders.resources import ResourcesSpider
from seoscraper.spiders.my_spider import MySpider

qfiles = deque()
configure_logging()
runner = CrawlerRunner(settings=get_project_settings())

@defer.inlineCallbacks
def crawl():
    #yield runner.crawl(MySpider)
    
    yield runner.crawl(SeoScraperSpider, 
        domains="seotrafico.com", 
        urls="/Users/antoinebrunel/Downloads/url_list.csv", 
        sitemapurls="http://seotrafico.com/sitemap.xml")
    #yield runner.crawl(ResourcesSpider, domains='seotrafico.com', queue=qfiles)
    reactor.stop()

crawl()
reactor.run() # the script will block here until the last crawl call is finished
