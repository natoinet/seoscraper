from urllib.parse import urljoin, urlparse

import pymongo
from pymongo import MongoClient

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import SitemapSpider, CrawlSpider, Rule

from seoscraper.items import UrlItem, PageMapItem

class SeoScraperSpider(SitemapSpider, CrawlSpider):
    name = "minime_html"

    #start_urls = ['https://seotrafico.com']
    #rules = ( Rule(LinkExtractor(allow=('', )), callback='parse_item'), )
    sitemap_rules = [ ('/', 'parse_item'), ]

    def __init__(self, domains=None, urls=None, sitemaps=None, follow=False, resources=False, links=False, *args, **kwargs):
        super(SeoScraperSpider, self).__init__(*args, **kwargs)

        self.follow = bool(follow)
        self.resources = bool(resources)
        self.links = bool(links)
        self.handle_httpstatus_list = range( 302, 511 )

        # Dynamically setting rules
        SeoScraperSpider.rules = ( Rule(LinkExtractor(allow=('', )), callback='parse_item', follow=self.follow), )
        super(SeoScraperSpider, self)._compile_rules()

        if (domains is not None):
            self.allowed_domains = [domains]

        if (sitemaps is not None):
            self.sitemap_urls = [sitemaps]

        if (urls is not None):
            with open(urls) as csv_file:
                self.start_urls = [url.strip() for url in csv_file.readlines()]
                self.logger.debug('__init__ %s', len(self.start_urls))

    def start_requests(self):
        # Required for SitemapSpider
        requests = list(super(SeoScraperSpider, self).start_requests())

        requests += [Request(url, self.parse_item) for url in self.start_urls]
        return requests

    def parse_item(self, response):
        try:
            self.logger.debug('parse %s', response.url)

            for request in self.yield_html(response):
                yield request

            # CrawlSpider defines this method to return all scraped urls.
            if (self.follow is True):
                yield from self.parse(response)
        except AttributeError as e:
            self.logger.exception("AttributeError exception")
        except Exception as e:
            self.logger.exception("Parse Exception")

    def yield_html(self, response):
        content_type = response.headers.get('Content-Type').decode(encoding='utf-8')
        self.logger.debug('yield_html content_type %s', content_type)

        item = UrlItem()
        item['url'] = response.url
        item['item_type'] = type(item)
        item['status'] = response.status
        item['content_size'] = response.headers.get('Content-Length', len(response.body)).decode(encoding='utf-8')
        item['content_type'] = content_type

        if 'html' in content_type:
            item['doc'] = {
                'source_url' : [ u for u in response.meta.get('redirect_urls', u'') ],
                'redirections' : response.meta.get('redirect_times', 0),
                'redirect_status' : response.meta.get('redirect_status', u''),
                'title' : response.xpath('//title/text()').extract(),
                'desc' : response.xpath('//meta[@name="description"]/@content').extract(),
                'h1' : response.xpath('//h1/text()').extract(),
                'robots' : response.xpath('//meta[@name="robots"]/@content').extract(),
                'canonical' : urljoin(response.url, response.xpath('//link[@rel="canonical"]/@href').extract_first()),
            }

            if (self.resources is True):
                self.logger.debug('yield_html crawl_resources is True %s', content_type)                
                # Extract href attribute        
                for request in self.yield_attributes(response, '@href', None):
                    yield request

                # Extract src attribute        
                for request in self.yield_attributes(response, '@src', None):
                    yield request
            elif (self.links is True):
                for request in self.yield_attributes(response, '@href', '//a'):
                    yield request
                

        yield item

        '''
        DISABLED FOR POSTGRE
        yield {
            'source_url' : [ urlparse(u) for u in response.meta.get('redirect_urls', u'') ],
            'url' : urlparse(response.url),
            'redirections' : response.meta.get('redirect_times', 0),
            'redirect_status' : response.meta.get('redirect_status', u''),
            'status' : response.status,
            'title' : response.xpath('//title/text()').extract(),
            'desc' : response.xpath('//meta[@name="description"]/@content').extract(),
            'h1' : response.xpath('//h1/text()').extract(),
            'robots' : response.xpath('//meta[@name="robots"]/@content').extract(),
            'content_type' : response.headers.get('Content-Type').decode(encoding='utf-8'),
            'content_size' : response.headers.get('Content-Length', len(response.body)).decode(encoding='utf-8'),
            'canonical' : urlparse(urljoin(response.url, response.xpath('//link[@rel="canonical"]/@href').extract_first())),
            'links' : [ { 
                            'href' : urlparse( urljoin(response.url, link.xpath('@href').extract_first() ) ),
                            'rel' : link.xpath('@rel').extract_first(), 
                            'text' : link.xpath('text()').extract_first() 
                        }
                        for link in response.xpath("//a") ],
            'resources' : [ { 'src' : urlparse(u) } for u in resources ],
            'images' : [ { 
                            'src' : urljoin(response.url, image.xpath('@src').extract_first()), 
                            'alt' : image.xpath('@alt').extract_first(), 
                            'title' : image.xpath('@title').extract_first(), 
                            'width' : image.xpath('@width').extract_first(), 
                            'height' : image.xpath('@height').extract_first() 
                        }
                        for image in images ]
        }
        '''

    def yield_attributes(self, response, attribute, element):
        try:
            if (element is None):
                ex_attribute = "//*[%s]" % attribute
            else:
                ex_attribute = element + "[%s]" % attribute

            for href_element in response.xpath(ex_attribute):
                link = urljoin( response.url, href_element.xpath(attribute).extract_first() )

                if (self.different_url(response.url, link) is True):
                    item = PageMapItem()
                    item['url'] = response.url
                    item['item_type'] = type(item)
                    item['link'] = link
                    # normalize-space allows to prevent \r\n characters
                    item['value'] = href_element.xpath('normalize-space(../text())').extract_first()
                    yield Request(link, callback=self.parse_item)
                    yield item

        except Exception as e:
            self.logger.exception("yield_attributes Exception")

    def different_url(self, url, link):
        parsed_url = urlparse( url )
        linked_url = urlparse( link )
        
        return ( (parsed_url.scheme != linked_url.scheme) 
            or (parsed_url.netloc != linked_url.netloc) 
            or (parsed_url.path != linked_url.path) 
            or (parsed_url.params != linked_url.params) 
            or (parsed_url.query != linked_url.query) )
