import logging

from seoscraper.items import UrlItem
from seoscraper.utils.misc import get_url_item, get_url_item_doc


def errback(failure):
    # log all failures
    logging.error(repr(failure))

    request = None
    value = None
    response = None
    error_message = None
    traceback = None

    if ( "request" in dir(failure) ):
        request = failure.request

    if ( "value" in dir(failure) ):
        value = failure.value

        if ( "response" in dir(failure.value) ):
            response = failure.value.response

    if ( "getErrorMessage" in dir(failure) ):
        error_message = failure.getErrorMessage()

    #if ( "getTraceback" in  dir(failure) ):
    #    traceback = failure.getTraceback()

    logging.error('Errback: request%s - value:%s - response:%s - error_message:%s - traceback:%s', str(request), str(value), str(response), str(error_message), str(traceback))

    return get_url_item_exception(request, value, response, error_message, traceback)
         

    '''
    # in case you want to do something special for some errors,
    # you may need the failure's type:

    if failure.check(RobotsTxtError):
        # From CustomRobotsTxtMiddleware downloader middleware
        request = failure.request
        logging.error('RobotsTxtError on %s', request.url)
        
    elif failure.check(HttpError):
        # these exceptions come from HttpError spider middleware
        # you can get the non-200 response
        response = failure.value.response
        logging.error('HttpError on %s %s', response.url, response.status)

    elif failure.check(DNSLookupError):
        # this is the original request
        request = failure.request
        logging.error('DNSLookupError on %s', request.url)

    elif failure.check(TimeoutError, TCPTimedOutError):
        request = failure.request
        logging.error('TimeoutError on %s', request.url)

    elif failure.check(IgnoreRequest):
        request = failure.request
        logging.error('IgnoreRequest on %s: -ErrorMessage:%s -Traceback:%s, value', request.url, failure.getErrorMessage(), failure.getTraceback(), repr(failure.value))

    else:
        logging.error('IgnoreRequest on %s %s', request.url, dir(failure))
    '''


def get_url_item_exception(request, value, response, error_message, traceback):
    url_item = UrlItem()
    doc = {}
    doc['request'] = repr(request)
    doc['value'] = repr(value)
    doc['response'] = repr(response)
    doc['ErrorMessage'] = error_message
    doc['Traceback'] = traceback

    if request:
        url_item['url'] = request.url
        doc['request_url'] = request.url

    if response:
        url_item = get_url_item(response)
        doc.update( get_url_item_doc(response) )

    url_item['doc'] = doc

    return url_item

