from urllib.parse import urlparse

from scrapy.spiders import Spider
from scrapy import Request

#from seoscraper.items import SeoLinkItem

class CheckExternalLinksSpider(Spider):
    name = "minime_linkchecker"

    def __init__(self, domains=None, urls=None, *args, **kwargs):
        super(CheckExternalLinksSpider, self).__init__(*args, **kwargs)
        self.handle_httpstatus_list = range( 400, 511 )
        self.hrefdomains = [domains]

        with open(urls) as csv_file:
            self.start_urls = [url.strip() for url in csv_file.readlines()]

    def parse(self, response):
        try:
            self.logger.info('parse')
        
            if response.status in self.handle_httpstatus_list:
                return {
                    'source' : response.url,
                    'status' : response.status
                }
                '''
                item = SeoLinkItem()
                item['source'] = response.url
                item['status'] = response.status

                return item
                '''
                

            # Get all the links
            a_list = response.xpath("//a")

            for a_link in a_list:
                link_href = a_link.xpath('@href').extract_first()
                if (urlparse(link_href).netloc in self.hrefdomains):
                    self.logger.info('parse> domain is present')
                    yield {
                        'source' : response.url,
                        'href' : link_href,
                        'hreflang' : a_link.xpath('@hreflang').extract_first(),
                        'rel' : a_link.xpath('@rel').extract_first(),
                        'title' : a_link.xpath('@title').extract_first(),
                        'target' : a_link.xpath('@target').extract_first(),
                        'media_type' : a_link.xpath('@media_type').extract_first(),
                        'download' : a_link.xpath('@download').extract_first()
                    }

                    '''
                    item = SeoLinkItem()
                    item['source'] = response.url
                    item['href'] = link_href
                    item['hreflang'] = a_link.xpath('@hreflang').extract_first()
                    item['rel'] = a_link.xpath('@rel').extract_first()
                    item['title'] = a_link.xpath('@title').extract_first()
                    item['target'] = a_link.xpath('@target').extract_first()
                    item['media_type'] = a_link.xpath('@media_type').extract_first()
                    item['download'] = a_link.xpath('@download').extract_first()
                    item['media'] = a_link.xpath('@media').extract_first()
                    self.logger.info('parse> domain is present -DONE')
                    yield item
                    '''

        except AttributeError as e:
            self.logger.exception("AttributeError exception")
        except Exception as e:
            self.logger.exception("Parse Exception")
