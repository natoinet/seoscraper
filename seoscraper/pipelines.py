import logging
import json

import psycopg2

from seoscraper.items import UrlItem, PageMapItem

class PostgreMultiplePipeline(object):
    def __init__(self):
        self.connection = psycopg2.connect(host='localhost', database='seoscraperdb', user='antoinebrunel')

    def process_item(self, item, spider):
        # check item type to decide which table to insert
        try:
            #self.cursor = self.connection.cursor()
            
            with self.connection as connection:
                with self.connection.cursor() as cursor:
                    if type(item) is UrlItem:
                        cursor.execute("""INSERT INTO urljson (url, status, content_type, content_size, doc) VALUES(%s, %s, %s, %s, %s)""", 
                            (   item.get('url', ''), 
                                int(item.get('status', 0)), 
                                item.get('content_type', ''), 
                                int(item.get('content_size', 0)),
                                json.dumps(item.get('doc', '')),
                                )
                        )

                    elif type(item) is PageMapItem:
                        cursor.execute("""INSERT INTO pagemap (url, link, value, rel) VALUES(%s, %s, %s, %s)""", (item.get('url'), item.get('link'), item.get('value'), item.get('rel'),))

                    connection.commit()
        except:
            logging.exception("Pipeline Error %s %s", item.get('url', ''), item.get('doc', ''))
        return item
