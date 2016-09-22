import logging

from scrapy.dupefilters import RFPDupeFilter

class CustomURLFilter(RFPDupeFilter):

    def __init__(self, path=None, debug=False):
        #RFPDupeFilter.__init__(self, path, debug)
        super(CustomURLFilter, self).__init__(path, debug)

    def request_seen(self, request):
        #RFPDupeFilter.request_seen(self, request)
        request_seen = super(CustomURLFilter, self).request_seen(request)
        redirect_urls = request.meta.get('redirect_urls', u'')

        # Do not apply the filter for urls with redirections
        # Testing internal redirections will never be filtered 
        # http://example.com/1 request_seen=False => http://example.com/2 request_seen=False 
        # http://example.com/1 filtered the 2nd time: request_seen=True
        if ( request_seen and ( len(redirect_urls) ) > 0 ):
            request_seen = False

        return request_seen
