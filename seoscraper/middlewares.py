from scrapy.downloadermiddlewares.redirect import RedirectMiddleware


class CustomRedirectMiddleware(RedirectMiddleware):
    """Handle redirection of requests based on response status and meta-refresh html tag"""
    
    def process_response(self, request, response, spider):
        #Get the redirect status codes
        request.meta.setdefault('redirect_status', []).append(response.status)
        response = super(CustomRedirectMiddleware, self).process_response(request, response, spider)
        return response
