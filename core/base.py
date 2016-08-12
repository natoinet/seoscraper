from envparse import env
import psycopg2

env.read_envfile()
PG_HOST = env.str('PG_HOST')
PG_DB = env.str('PG_DATABASE')
PG_USER = env.str('PG_USER')

def delete_table(table):
    # Delete all data in the tables
    with psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER) as connection:
        cur = connection.cursor()
        cur.execute( "delete from " + table)
        #cur.execute( """delete from %s""", (table,) )
        #cur.execute("delete from urljson")
        #cur.execute("delete from pagemap")

def db_to_csv(query, tofile):
    with psycopg2.connect(host=PG_HOST, database=PG_DB, user=PG_USER) as connection:
        cur = connection.cursor()
        outputquery = "COPY ({0}) TO STDOUT WITH CSV HEADER".format(query)

        with open(tofile, 'w') as f: #"/Users/antoinebrunel/Downloads/res_url_list_links_cirh.csv"
            cur.copy_expert(outputquery, f)
