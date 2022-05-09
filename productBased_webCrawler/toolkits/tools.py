import xxhash
import pymysql
from .. import const

def connect_mysql():
    connect = pymysql.connect(
        host=const.MYSQL_HOST,
        db=const.MYSQL_DATABASE,
        user=const.MYSQL_USERNAME,
        passwd=const.MYSQL_PASSWORD,
        port=const.MYSQL_PORT,
        charset='utf8'
    )
    cursor = connect.cursor()
    print("Connect to Mysql.")
    return connect, cursor

def close_mysql(connect,cursor):
    connect.close()
    cursor.close()
    print("Close connection of Mysql.")

def hash_url(url):
    xx_url = xxhash.xxh64(url).intdigest()
    return xx_url

def not_crawled_urls(cursor, urls):
    xx_urls = [hash_url(url) for url in urls]
    sql = "select xx_url from crawled_urls where xx_url in ({})".format(",".join([str(xx_url) for xx_url in xx_urls]))
    cursor.execute(sql)
    crawled_xx_urls = [result[0] for result in cursor.fetchall()]
    ll = []
    not_crawled_xx_urls = list(set(xx_urls) - set(crawled_xx_urls))
    for url,xx_url in zip(urls,xx_urls):
        if xx_url in not_crawled_xx_urls:
            ll.append((url,xx_url))
    return ll
