# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SeoScraperItem(scrapy.Item):
    source_url = scrapy.Field()
    final_url = scrapy.Field()
    redirections = scrapy.Field()
    redirect_status = scrapy.Field()
    status = scrapy.Field()
    robots = scrapy.Field()
    title = scrapy.Field()
    desc = scrapy.Field()
    h1 = scrapy.Field()
    image_urls = scrapy.Field()
    file_type = scrapy.Field()