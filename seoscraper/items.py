import scrapy

class ScraperItem(scrapy.Item):
    item_type = scrapy.Field()

class UrlItem(ScraperItem):
    url = scrapy.Field()
    status = scrapy.Field()
    content_type = scrapy.Field()
    content_size = scrapy.Field()
    doc = scrapy.Field()

class PageMapItem(ScraperItem):
    url = scrapy.Field()
    link = scrapy.Field()
    anchor = scrapy.Field()
    alt = scrapy.Field()
    title = scrapy.Field()
    rel = scrapy.Field()
    link_type = scrapy.Field()
