import logging

from scrapy import Request
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.spidermiddlewares.offsite import OffsiteMiddleware
from scrapy.utils.httpobj import urlparse_cached


class CustomRedirectMiddleware(RedirectMiddleware):
    """Handle redirection of requests based on response status and meta-refresh html tag"""
    
    def process_response(self, request, response, spider):
        # Get the redirect status codes
        request.meta.setdefault('redirect_status', []).append(response.status)
        response = super(CustomRedirectMiddleware, self).process_response(request, response, spider)

        return response

class CustomOffsiteMiddleware(OffsiteMiddleware):
    def should_follow(self, request, spider):
        should_follow_request = super(CustomOffsiteMiddleware, self).should_follow(request, spider)

        referer = Request(request.headers.get('Referer', '').decode(encoding='utf-8'))
        should_follow_referer = super(CustomOffsiteMiddleware, self).should_follow(referer, spider)

        '''
        regex = self.host_regex
        referer = Request(request.headers.get('Referer', '').decode(encoding='utf-8'))
        host = urlparse_cached(referer).hostname or ''

        should_follow_referer = regex.search(host)
        '''

        return (should_follow_request or should_follow_referer)

