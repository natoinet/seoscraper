from urllib.parse import urljoin, urlparse

from seoscraper.items import UrlItem, PageMapItem


def get_url_item(response):
    url_item = UrlItem()
    url_item['url'] = response.url
    url_item['status'] = response.status
    url_item['content_size'] = response.headers.get('Content-Length', len(response.body)).decode(encoding='utf-8')
    url_item['content_type'] = get_content_type(response)
    return url_item


def get_url_item_doc(response):
    referer = get_referer(response)
    return {
        'redirect_urls' : [ u for u in response.meta.get('redirect_urls', u'') ],
        'redirections' : response.meta.get('redirect_times', 0),
        'redirect_status' : response.request.meta.get('redirect_status', u''),
        'title' : response.xpath('//title/text()').extract_first(),
        'desc' : response.xpath('//meta[@name="description"]/@content').extract_first(),
        'h1' : response.xpath('//h1/text()').extract_first(),
        'robots' : response.xpath('//meta[@name="robots"]/@content').extract_first(),
        'canonical' : urljoin(response.url, response.xpath('//link[@rel="canonical"]/@href').extract_first()),
        'referer' : referer,
    }


def get_css_pagemap_item(response, joined_url):
    item = PageMapItem()
    item['url'] = response.url
    item['link_type'] = 'css'
    item['link'] = joined_url
    item['anchor'] = ''
    item['rel'] = ''
    item['alt'] = ''
    item['title'] = ''
    return item


def get_attribute_pagemap_item(response, link):
    item = PageMapItem()
    item['url'] = response.url
    #item['link_type'] = element.xpath("name()").extract_first()
    item['link'] = link.url
    item['anchor'] = link.text
    item['rel'] = link.nofollow
    # normalize-space allows to prevent \r\n characters
    #item['anchor'] = element.xpath('normalize-space(text())').extract_first()
    #item['rel'] = element.xpath('@rel').extract_first()
    #item['alt'] = element.xpath('@alt').extract_first()
    #item['title'] = element.xpath('@title').extract_first()
    return item


def get_referer(response):
    referer = response.request.headers.get('Referer', None)
    if referer is not None:
        referer = referer.decode(encoding='utf-8')
    return referer


def get_content_type(response):
    content_type = response.headers.get('Content-Type', u'')
    if content_type is not u'':
        content_type = content_type.decode(encoding='utf-8')
    return content_type


def different_url(url, link):
    parsed_url = urlparse( url )
    linked_url = urlparse( link )
    return ( (parsed_url.scheme != linked_url.scheme) 
        or (parsed_url.netloc != linked_url.netloc) 
        or (parsed_url.path != linked_url.path) 
        or (parsed_url.params != linked_url.params) 
        or (parsed_url.query != linked_url.query) )
