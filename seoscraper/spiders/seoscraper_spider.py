from urllib.parse import urljoin, urlparse
#from urlparse import urljoin

from scrapy.spiders import Spider
from scrapy import Request

#from seoscraper.items import SeoScraperItem

class SeoScraperSpider(Spider):
    name = "minime_scraper"

    def __init__(self, domains=None, urls=None, *args, **kwargs):
        super(SeoScraperSpider, self).__init__(*args, **kwargs)

        self.handle_httpstatus_list = range( 302, 511 )
        self.allowed_domains = [domains]

        with open(urls) as csv_file:
            self.start_urls = [url.strip() for url in csv_file.readlines()]

    def parse(self, response):
        #log.msg('Hi, this is a response %s and a row!: %r' % str(response.status) % row)
        #item = SeoScraperItem()

        try:
            self.logger.info('parse')

            '''
            item['source_url'] = response.meta.get('redirect_urls', u'')
            item['final_url'] = response.url
            item['redirections'] = response.meta.get('redirect_times', 0)
            item['redirect_status'] = response.meta.get('redirect_status', u'')
            item['status'] = response.status
            item['title'] = response.xpath('//title/text()').extract()
            item['desc'] = response.xpath('//meta[@name="description"]/@content').extract()
            item['h1'] = response.xpath('//h1/text()').extract()
            item['robots'] = response.xpath('//meta[@name="robots"]/@content').extract()
            '''

            '''
            # Resolves the "Missing scheme in request URL" when url misses http for example
            #image_urls = [ urljoin(response.url, u) for u in response.xpath("//img/@src").extract() ]
            #script_urls = [ urljoin(response.url, u) for u in response.xpath('//script/@src').extract()]
            #link_urls = [ urljoin(response.url, u) for u in response.xpath("//link/@href").extract() ]
            #item['file_type'] = 'html'

            for request in self.yield_resources(response, image_urls):
                yield request

            for request in self.yield_resources(response, link_urls):
                yield request

            for request in self.yield_resources(response, script_urls):
                yield request
            '''

            '''
            resources = [ urljoin(response.url, u) for u in response.xpath("//img/@src").extract() ]
            resources.extend( [ urljoin(response.url, u) for u in response.xpath('//script/@src').extract() ] )
            resources.extend( [ urljoin(response.url, u) for u in response.xpath("//link/@href").extract() ] )
            
            for request in self.yield_resources(response, resources):
                yield request

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
                'a_href' : [ urlparse(urljoin(response.url, u)) for u in response.xpath("//a/@href").extract() ],
                'resources' : [ urlparse(u) for u in resources ]
            }
            '''

            for request in self.yield_html(response):
                yield request

        except AttributeError as e:
            self.logger.exception("AttributeError exception")
        except Exception as e:
            self.logger.exception("Parse Exception")

    def yield_html(self, response):
        images = response.xpath("//img")
        img_extraction = [ urljoin(response.url, u) for u in images.xpath("@src").extract() ]

        for request in self.request_resources(response, img_extraction):
            yield request

        resources = ( [ urljoin(response.url, u) for u in response.xpath('//script/@src').extract() ] )
        resources.extend( [ urljoin(response.url, u) for u in response.xpath("//link/@href").extract() ] )

        for request in self.request_resources(response, resources):
            yield request

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
                            'href' : link.xpath('@href').extract_first(), 
                            'rel' : link.xpath('@rel').extract_first(), 
                            'text' : link.xpath('text()').extract_first() 
                        }
                        for link in response.xpath("//a") ],
            'resources' : [ urlparse(u) for u in resources ],
            'images' : [ { 
                            'src' : image.xpath('@src').extract_first(), 
                            'alt' : image.xpath('@alt').extract_first(), 
                            'title' : image.xpath('@title').extract_first(), 
                            'width' : image.xpath('@width').extract_first(), 
                            'height' : image.xpath('@height').extract_first() 
                        }
                        for image in images ]
        }

    def request_resources(self, response, urls):
        self.logger.info('request_resources')
        for url in urls:
            self.logger.debug('request_resources url %s', url)
            request = Request(url, callback=self.parse_resource)
            # Adds the source url for this resource
            #request.meta['source_url'] = urlparse(response.url)
            yield request

    def parse_resource(self, response):
        self.logger.info('parse_resource')

        try:
            content_type = response.headers.get('Content-Type').decode(encoding='utf-8')
            status =  response.status
            if status in self.handle_httpstatus_list:
                yield {
                    'url' : urlparse(response.url),
                    'status' : response.status
                }
            elif 'html' not in content_type:
                yield {
                    'url' : urlparse(response.url),
                    'status' : response.status,
                    'content_type' : content_type,
                    'content_size' : int(response.headers.get('Content-Length', len(response.body)))
                }
        except Exception as e:
            self.logger.exception("parse_resource Exception")
