import logging

from scrapy import Request
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.downloadermiddlewares.robotstxt import RobotsTxtMiddleware
from scrapy.spidermiddlewares.offsite import OffsiteMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.http import Response

from seoscraper.items import UrlItem

class CustomRedirectMiddleware(RedirectMiddleware):
    """Handle redirection of requests based on response status and meta-refresh html tag"""
    
    def process_response(self, request, response, spider):
        # Get the redirect status codes
        request.meta.setdefault('redirect_status', []).append(response.status)
        response = super(CustomRedirectMiddleware, self).process_response(request, response, spider)

        return response

class CustomRobotsTxtMiddleware(RobotsTxtMiddleware):
    """Capture robots.txt limitations"""
    
    def process_exception(self, request, exception, spider):
        # if exception type is IgnoreRequest, then return a response
        if (isinstance(exception, IgnoreRequest) and isinstance(self, CustomRobotsTxtMiddleware)):
            return Response(request.url, status=429, headers={'Content-Type' : 'Blocked'})


class CustomOffsiteMiddleware(OffsiteMiddleware):
    """Change offsite filtering behaviour: Do not filter offsite urls if the referer is onsite"""

    def should_follow(self, request, spider):
        should_follow_request = super(CustomOffsiteMiddleware, self).should_follow(request, spider)

        referer = Request(request.headers.get('Referer', '').decode(encoding='utf-8'))
        should_follow_referer = super(CustomOffsiteMiddleware, self).should_follow(referer, spider)

        return (should_follow_request or should_follow_referer)

