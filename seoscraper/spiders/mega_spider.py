from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import SitemapSpider, CrawlSpider, Rule

class MegaSpider(SitemapSpider, CrawlSpider):
    name = "megaspider"

    rules = ( Rule(LinkExtractor(allow=('', )), callback='parse_item', follow=True), )
    sitemap_rules = [ ('/', 'parse_item'), ]
    sitemap_urls = ['https://seotrafico.com/sitemap.xml']
    start_urls = ['https://seotrafico.com']
    allowed_domains = ['seotrafico.com']

    def parse_item(self, response):
        yield { 'url' : response.url,
            'title' : response.xpath('//title/text()').extract() }

        # Return to CrawlSpider that will crawl them
        yield from self.parse(response)
