import logging
import json

from envparse import env
import psycopg2
import treq

from seoscraper.items import UrlItem, PageMapItem
from core.base import delete_table

class PostgreMultiplePipeline(object):
    def __init__(self):
        #self.connection = psycopg2.connect(host='localhost', database='seoscraperdb', user='antoinebrunel')
        env.read_envfile()
        self.connection = psycopg2.connect(host=env.str('PG_HOST'), database=env.str('PG_DATABASE'), user=env.str('PG_USER'))

    def process_item(self, item, spider):
        # check item type to decide which table to insert
        try:
            #self.cursor = self.connection.cursor()
            
            with self.connection as connection:
                with self.connection.cursor() as cursor:
                    if type(item) is UrlItem:
                        json_doc = item.get('doc', '')

                        cursor.execute("""INSERT INTO urljson (url, status, content_type, content_size, doc) VALUES(%s, %s, %s, %s, %s)""", 
                            (   item.get('url', ''), 
                                int(item.get('status', 0)), 
                                item.get('content_type', ''), 
                                int(item.get('content_size', 0)),
                                json.dumps( item.get('doc', '') ),
                                )
                        )

                        if (json_doc != ''):
                            url = json_doc.get('referer', '')
                            links = json_doc.get('redirect_urls', [])

                            if (len(links) > 0 and url != ''):
                                link_final = item.get('url', '')

                                logging.info("process_item pipeline: url:%s links:%s link_final:%s", url, str(links), link_final)

                                #Then update the pagemap, add link_final
                                cursor.execute("""UPDATE pagemap SET link_final=%s WHERE link=%s AND url=%s""", (link_final, links[0], url))

                    elif type(item) is PageMapItem:
                        cursor.execute("""INSERT INTO pagemap (url, link, value, rel) VALUES(%s, %s, %s, %s)""", (item.get('url'), item.get('link'), item.get('value'), item.get('rel'),))

                    connection.commit()
        except:
            logging.exception("Pipeline Error %s %s", item.get('url', ''), item.get('doc', ''))
        return item

class PageSpeedPipeline(object):
    PAGESPEED_URL = 'https://www.googleapis.com/pagespeedonline/v2/runPagespeed'
    
    def __init__(self):
        #self.connection = psycopg2.connect(host='localhost', database='seoscraperdb', user='antoinebrunel')
        env.read_envfile()
        self.connection = psycopg2.connect(host=env.str('PG_HOST'), database=env.str('PG_DATABASE'), user=env.str('PG_USER'))
        self.api_key = env.str('GOOGLE_PAGESPEED_API_KEY')
        delete_table('pagespeed')
        logging.debug('__init__:' + self.PAGESPEED_URL + self.api_key)

    def process_item(self, item, spider):
        try:
            if type(item) is UrlItem:
                # Call Pagespeed API
                url = item.get('url', '')
                params={'url' : url, 'key' : self.api_key }
                #logging.debug('PageSpeedPipeline:' + self.PAGESPEED_URL + str(params))

                treq.get(self.PAGESPEED_URL, params=params).addCallback(self.api_done)
                #r = requests.get(self.PAGESPEED_URL, params=params)

                '''
                response = yield treq.get(self.PAGESPEED_URL, params=params)
                code = yield treq.code(response)

                if (code is 200):
                    result = yield treq.text(response)

                    with self.connection.cursor() as cursor:
                        # Store result in DB
                        cursor.execute("""INSERT INTO pagespeed (url, result) VALUES(%s, %s)""", ( url, result ) )
                        self.connection.commit()
                '''
                            
        except:
            logging.exception("PageSpeedPipeline Error %s", item.get('url', ''))
            
        return item

    def api_done(self, response):
        try:
            #logging.info( "PageSpeedPipeline API_Done %s %s", str(response.code), str(response.request.absoluteURI.decode('utf-8')) )
            logging.info( "PageSpeedPipeline API_Done %s", str(response.code) )

            response.json().addCallback(self.store_result)

            '''
            if (response.code is 200):
                with self.connection.cursor() as cursor:
                    # Store result in DB
                    cursor.execute("""INSERT INTO pagespeed (url, result) VALUES(%s, %s)""", ( response.request.absoluteURI.decode('utf-8'), response.json() ))
                    self.connection.commit()
            '''
        except:
            logging.exception("PageSpeedPipeline API_Done Error")

    def store_result(self, result_json):
        try:
            logging.info( "PageSpeedPipeline store_result %s", str(result_json) )

            with self.connection.cursor() as cursor:
                # Store result in DB
                cursor.execute("""INSERT INTO pagespeed (url, result) VALUES(%s, %s)""", ( result_json['id'], json.dumps(result_json, '') ))
                self.connection.commit()

        except:
            logging.exception("PageSpeedPipeline store_result Error")
        