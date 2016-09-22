import re
from urllib.parse import urljoin, urlparse

from twisted.internet.error import ConnectionRefusedError, DNSLookupError, TCPTimedOutError, TimeoutError

from scrapy import Request
from scrapy.exceptions import IgnoreRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import SitemapSpider, CrawlSpider, Rule
from scrapy.spidermiddlewares.httperror import HttpError

from seoscraper.middlewares import RobotsTxtError
from seoscraper.items import UrlItem, PageMapItem
from seoscraper.utils.misc import get_referer, get_content_type, different_url
from seoscraper.utils.misc import get_url_item, get_url_item_doc, get_css_pagemap_item, get_attribute_pagemap_item
from seoscraper.utils.errors import errback

class SeoScraperSpider(SitemapSpider, CrawlSpider):
    name = "minime_html"

    sitemap_rules = [ ('/', 'parse_item'), ]

    def __init__(self, domains=None, urls=None, sitemaps=None, follow=False, resources=False, links=False, *args, **kwargs):
        super(SeoScraperSpider, self).__init__(*args, **kwargs)

        self.logger.debug('__init__ domains:%s, urls:%s, sitemaps:%s, follow:%s, resources:%s, links:%s', domains, urls, sitemaps, follow, resources, links)

        self.follow = bool(follow)
        self.resources = bool(resources)
        self.links = bool(links)
        #self.handle_httpstatus_list = [-1, -2, -998, -999] #+ list(range( 302, 511 ))

        # Dynamically setting rules
        SeoScraperSpider.rules = ( Rule(LinkExtractor(allow=('', )), callback='parse_item', follow=self.follow), )
        super(SeoScraperSpider, self)._compile_rules()

        if (domains is not None):
            self.allowed_domains = [domains]
        #self.allowed_domains = [domains]

        if (sitemaps is not None):
            self.sitemap_urls = [sitemaps]

        if (urls is not None):
            with open(urls) as csv_file:
                self.start_urls = [url.strip() for url in csv_file.readlines()]
                self.logger.debug('__init__ %s', len(self.start_urls))


    def _parse_sitemap(self, response):
        sitemapspider_requests = super(SeoScraperSpider, self)._parse_sitemap(response)

        # Adds error management to requests
        for request in sitemapspider_requests:
            yield request.replace(errback=errback)


    def start_requests(self):
        # Required for SitemapSpider
        sitemapspider_requests = list( super(SeoScraperSpider, self).start_requests() )

        # Adds errback to sitemap requests
        requests = [ request.replace(errback=errback) for request in sitemapspider_requests ]

        # Referer set as csv for urls from the csv file
        # dont_filter to True in case urls have been previously crawled from the sitemap
        #requests += [ Request(url, self.parse_item, headers={'Referer':'File'}, dont_filter=True) for url in self.start_urls ]
        requests += [ Request(url, self.parse_item, headers={'Referer':'File'}, dont_filter=True, errback=errback) for url in self.start_urls ]
        return requests


    def _requests_to_follow(self, response):
        # Required for SitemapSpider
        crawlspider_requests = list( super(SeoScraperSpider, self)._requests_to_follow(response) )

        # Adds errback to sitemap requests
        for request in crawlspider_requests:
            yield request.replace(errback=errback)


    def parse_item(self, response):
        try:
            self.logger.debug('parse_item %s', response.url)

            for request in self.yield_html(response):
                yield request

            # CrawlSpider defines this method to return all scraped urls.
            if (self.follow is True):
                yield from self.parse(response)
        except AttributeError as e:
            self.logger.exception("AttributeError exception")
        except Exception as e:
            self.logger.exception("Parse Exception")


    '''
    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(RobotsTxtError):
            # From CustomRobotsTxtMiddleware downloader middleware
            request = failure.request
            self.logger.error('RobotsTxtError on %s', request.url)
            
        elif failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s %s', response.url, response.status)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

        elif failure.check(IgnoreRequest):
            request = failure.request
            self.logger.error('IgnoreRequest on %s: -ErrorMessage:%s -Traceback:%s, value', request.url, failure.getErrorMessage(), failure.getTraceback(), repr(failure.value))
        
        else:
            self.logger.error('IgnoreRequest on %s %s', request.url, dir(failure))
    '''


    def yield_html(self, response):
        content_type = get_content_type(response)
        url_item = get_url_item(response)
                
        #if response.flags == ['duplicate_redirection']:
        #    if (response.meta.get('redirect_urls', u'') is not u''):
        #        yield self.get_redirection_item(response)

        #elif 'html' in content_type:
        if 'html' in content_type:
            url_item['doc'] = get_url_item_doc(response)
            yield url_item

            '''
            if (response.meta.get('redirect_urls', u'') is not u''):
                yield self.get_redirection_item(response)
            '''

            if (self.resources is True):
                # Extract href attribute        
                for request in self.yield_attributes(response, None, '@href'):
                    yield request

                # Extract src attribute        
                for request in self.yield_attributes(response, None, '@src'):
                    yield request

            elif (self.links is True):
                for request in self.yield_attributes(response, '//a', '@href'):
                    yield request
        
        # Search for urls in string
        elif 'css' in content_type:
            #css_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', response.text)
            css_urls = re.findall('url\(([^)]+)\)', response.text)

            for css_url in css_urls:
                joined_url = urljoin(response.url, css_url.replace("'", "").replace('"', '') )                
                yield get_css_pagemap_item(response, joined_url)
                #yield Request(joined_url, callback=self.parse_item)
                yield Request(joined_url, callback=self.parse_item, errback=errback)

            yield url_item
        else:
            yield url_item


    def yield_attributes(self, response, element, attribute):
        try:
            if (element is None):
                ex_attribute = "//*[%s]" % attribute
            else:
                ex_attribute = element + "[%s]" % attribute

            for href_element in response.xpath(ex_attribute):
                link = urljoin( response.url, href_element.xpath(attribute).extract_first() )

                if ( different_url(response.url, link )):
                    yield get_attribute_pagemap_item(response, href_element, link)

                    if (self.follow is True):
                        #yield Request(link, callback=self.parse_item)
                        yield Request(link, callback=self.parse_item, errback=errback)
        except Exception as e:
            self.logger.exception("yield_attributes Exception")
