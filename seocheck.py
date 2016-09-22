import argparse
from datetime import datetime

from envparse import env
import psycopg2
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerProcess, CrawlerRunner

from core.base import delete_table, db_to_csv

env.read_envfile()
SCRAPY_SETTINGS_MODULE = env.str('SCRAPY_SETTINGS_MODULE')

parser = argparse.ArgumentParser(description='Check a domain and extracts the url list and pagemap.')
parser.add_argument('resultpath', type=str, help='Result path')
parser.add_argument('-d', '--domains', type=str, help='domain to check')
parser.add_argument('-s', '--sitemaps', type=str, help='website to check', default=None)  #Optional argument
parser.add_argument('-u', '--urls', type=str, help='Source file with an input list of urls if any', default=None) #Optional argument
parser.add_argument('-f', '--follow', help='if pagemap is required', action="store_true") #Optional argument
parser.add_argument('-r', '--resources', help='crawls all files', action="store_true") #Optional argument
parser.add_argument('-p', '--pagemap', help='if pagemap is required', action="store_true") #Optional argument
args = parser.parse_args()

print(args.domains, args.sitemaps, args.resultpath, args.urls, args.follow, args.pagemap, args.resources)

delete_table("urljson")
delete_table("pagemap")
delete_table("redirections")

# Crawl
configure_logging({'LOG_LEVEL' : 'DEBUG'})
process = CrawlerProcess(settings=get_project_settings())

process.crawl('minime_html', domains=args.domains, urls=args.urls,sitemaps=args.sitemaps, 
                follow=args.follow, resources=args.resources, links=args.pagemap)
process.start()

# Export => Combine results from pagemap & urllist
query = """select url, doc->'canonical' as canonical, status, doc->'robots' as robots, content_type, content_size, doc->'referer' as referer, doc->'title' as title, doc->'desc' as desc, doc->'h1' as h1, doc->'redirect_urls' as redirect_urls, doc->'redirect_status' as redir_status, doc->'redirections' as nb_redir from urljson"""
db_to_csv(query, args.resultpath + 'seocheck-' + str(datetime.now()) + '.csv')

query = """select pagemap.url, pagemap.link, pagemap.link_final, urljson.status from pagemap, urljson where pagemap.link=urljson.url or pagemap.link_final=urljson.url"""
db_to_csv(query, args.resultpath + 'seocheck-pagemap-' + str(datetime.now()) + '.csv')
