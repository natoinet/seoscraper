# -*- coding: utf-8 -*-
from urllib.parse import urljoin, urlparse

import pymongo
from pymongo import MongoClient


import scrapy
from scrapy import Request


class ResourcesSpider(scrapy.Spider):
    name = "minime_resources"
    allowed_domains = ["seotrafico.com"]
    '''
    start_urls = (
        'http://www.seotrafico.com/',
    )
    '''

    def __init__(self, domains=None, queue=None, *args, **kwargs):
        super(ResourcesSpider, self).__init__(*args, **kwargs)

        self.handle_httpstatus_list = range( 302, 511 )
        self.allowed_domains = [domains]

        self.collection = MongoClient().scrapy.my_items

        if (queue is not None):
            self.start_urls = [url for url in queue]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        self.logger.info('parse_resource %s', response.url)

        try:
            content_type = response.headers.get('Content-Type').decode(encoding='utf-8')
            status =  response.status
            if status in self.handle_httpstatus_list:
                result = self.collection.update_many( {"resources.src" : urlparse(response.url) },
                        { "$set" : { 'resources.$.src' : urlparse(response.url),
                                    'resources.$.status' : status } } )
                #self.logger.debug(response.url, str(result.modified_count) )

                '''
                yield {
                    'url' : response.url,
                    'status' : response.status
                }
                '''
            elif 'html' not in content_type:
                result = self.collection.update_many( {"resources.src" : urlparse(response.url) },
                        { "$set" : { 'resources.$.src' : urlparse(response.url),
                                    'resources.$.status' : status,
                                    'resources.$.content_type' : content_type,
                                    'resources.$.content_size' : int(response.headers.get('Content-Length', len(response.body)))
                                     } } )
                #self.logger.debug(response.url, str(result.modified_count) )
                
                '''
                yield {
                    'url' : response.url,
                    'status' : response.status,
                    'content_type' : content_type,
                    'content_size' : int(response.headers.get('Content-Length', len(response.body)))
                }
                '''
        except Exception as e:
            self.logger.exception("parse_resource Exception")
