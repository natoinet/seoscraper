import logging

from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.downloadermiddlewares.robotstxt import RobotsTxtMiddleware
from scrapy.spidermiddlewares.offsite import OffsiteMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.http import Response, Request
from scrapy.utils.misc import load_object

from seoscraper.items import UrlItem

class CustomRedirectMiddleware(RedirectMiddleware):
    """Handle redirection of requests based on response status and meta-refresh html tag"""

    def process_response(self, request, response, spider):
        #logging.info( 'CustomRedirectMiddleware url:%s request.errback:%s', request.url, str(request.errback) )
        
        # Get the redirect status codes
        request.meta.setdefault('redirect_status', []).append(response.status)
        response = super(CustomRedirectMiddleware, self).process_response(request, response, spider)

        return response

class RobotsTxtError(IgnoreRequest):
    """A robots.txt response was filtered"""

    def __init__(self, *args, **kwargs):
        super(RobotsTxtError, self).__init__(*args, **kwargs)

class CustomRobotsTxtMiddleware(RobotsTxtMiddleware):
    """Capture robots.txt limitations"""
    
    def process_exception(self, request, exception, spider):
        # if exception type is IgnoreRequest, then return a response
        if isinstance(exception, IgnoreRequest):
            #return Response(request.url, status=-1, headers={'Content-Type' : 'Blocked by robots.txt'})
            raise RobotsTxtError("Blocked by robots.txt")


class CustomOffsiteMiddleware(OffsiteMiddleware):
    """Change offsite filtering behaviour: Do not filter offsite urls if the referer is onsite"""

    def should_follow(self, request, spider):
        should_follow_request = super(CustomOffsiteMiddleware, self).should_follow(request, spider)

        referer = Request(request.headers.get('Referer', '').decode(encoding='utf-8'))
        should_follow_referer = super(CustomOffsiteMiddleware, self).should_follow(referer, spider)

        return (should_follow_request or should_follow_referer)


''' Use REDIRECT_MAX_TIMES in settings instead! http://doc.scrapy.org/en/latest/topics/settings.html#redirect-max-times
class CustomRedirectionLoopMiddleware(object):
    """Redirections Middleware to trace all redirections, even when the final url has already been crawled"""
    
    def __init__(self, max_redirection_depth):
        self.max_redir_depth = max_redirection_depth

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        #redir_depth_filter_cls = load_object(settings['MAX_REDIRECTION_DEPTH'])
        #redir_depth_filter = redir_depth_filter_cls.from_settings(settings)
        max_redirection_depth = settings['MAX_REDIRECTION_DEPTH']
        logging.info('CustomRedirectionLoopMiddleware Init MAX_REDIRECTION_DEPTH=%s', str(max_redirection_depth))
        return cls(max_redirection_depth)

    def process_request(self, request, spider):
        if len( request.meta.get('redirect_urls', u'') ) > self.max_redir_depth:
            raise IgnoreRequest("Reached max redirection depth")

    def process_exception(self, request, exception, spider):
        # if exception type is IgnoreRequest, then return a response
        if isinstance(exception, IgnoreRequest):
            return Response(request.url, status=-2, headers={'Content-Type' : 'Reached max redirection depth'})
'''

class CustomCatchExceptionMiddleware(object):
    def process_exception(self, request, exception, spider):
        # if an exception raised, then catch the url
        return Response( request.url, status=-999, headers={ 'Content-Type' : str(exception), 'Previous-Request' : str(request) } )

class CustomTestExceptionMiddleware1(object):
    def process_response(self, request, response, spider):
        raise IgnoreRequest("CustomTestExceptionMiddleware1")
        return response

    def process_exception(self, request, exception, spider):
        logging.info('CustomTestExceptionMiddleware1 process_exception url:%s request:%s exception:%s', request.url, str(request), str(exception))
        return Response( request.url, status=-998, headers={ 'Content-Type' : str(exception), 'Previous-Request' : str(request) } )

class CustomTestExceptionMiddleware2(object):
    def process_response(self, request, response, spider):
        raise IgnoreRequest("CustomTestExceptionMiddleware2")
        return response

    def process_exception(self, request, exception, spider):
        logging.info('CustomTestExceptionMiddleware2 process_exception url:%s request:%s exception: %s', request.url, str(request), str(exception))
        return Response( request.url, status=-999, headers={ 'Content-Type' : str(exception), 'Previous-Request' : str(request) } )
