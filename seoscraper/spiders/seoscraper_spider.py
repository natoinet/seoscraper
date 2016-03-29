from urllib.parse import urljoin

from scrapy.spiders import Spider
from scrapy import Request

from seoscraper.items import SeoScraperItem

class SeoScraperSpider(Spider):
    name = "minime"

    def __init__(self, domains=None, urls=None, *args, **kwargs):
        super(SeoScraperSpider, self).__init__(*args, **kwargs)

        self.handle_httpstatus_list = range( 400, 511 )
        self.allowed_domains = [domains]

        with open(urls) as csv_file:
            self.start_urls = [url.strip() for url in csv_file.readlines()]

    def parse(self, response):
        #log.msg('Hi, this is a response %s and a row!: %r' % str(response.status) % row)
        item = SeoScraperItem()

        try:
            item['source_url'] = response.meta.get('redirect_urls', u'')
            item['final_url'] = response.url
            item['redirections'] = response.meta.get('redirect_times', 0)
            item['redirect_status'] = response.meta.get('redirect_status', u'')
            item['status'] = response.status
            item['title'] = response.xpath('//title/text()').extract()
            item['desc'] = response.xpath('//meta[@name="description"]/@content').extract()
            item['h1'] = response.xpath('//h1/text()').extract()
            item['robots'] = response.xpath('//meta[@name="robots"]/@content').extract()
            # Resolves the "Missing scheme in request URL" when url misses http for example
            item['image_urls'] = [ urljoin(response.url, u) for u in response.xpath("//img/@src").extract() ]
            item['file_type'] = 'html'

            for image_url in item['image_urls']:
                request = Request(image_url, callback=self.parse_img)
                # Adds the source url for this image
                request.meta['source_url'] = response.url
                yield request

            #return item

        except AttributeError as e:
            self.logger.exception("AttributeError exception")
        except Exception as e:
            self.logger.exception("Parse Exception")

    def parse_img(self, response):
        item = SeoScraperItem()

        try:
            item['source_url'] = response.request.meta['source_url']
            item['final_url'] = response.url
            item['status'] = response.status
            item['file_type'] = 'image'
        except Exception as e:
            self.logger.exception("parse_img Exception")

        yield item
