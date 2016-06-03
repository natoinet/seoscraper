import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class MySpider(CrawlSpider):
    name = 'seotrafico.com'
    #allowed_domains = ['seotrafico.com']
    start_urls = ['https://seotrafico.com']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('', )), callback='parse_item'),
    )

    def parse_item(self, response):
        return { 'source_url' : response.meta.get('redirect_urls', u''),
            'final_url' : response.url,
            'title' : response.xpath('//title/text()').extract(),
            'description' : response.xpath('//meta[@name="description"]/@content').extract() }
