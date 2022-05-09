# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.exporters import JsonLinesItemExporter
from . import const

from datetime import datetime
import pytz
import pymysql
import os
import gzip
import shutil

class ProductbasedWebcrawlerPipeline:
    def process_item(self, item, spider):
        return item

class JsonPipeline:
    """
    This pipeline can save items into json file which is under the folder of the website.
    """
    timezone = pytz.timezone('Asia/Taipei')
    now = datetime.now(timezone).strftime('%Y-%m-%d-%H%M%S')
    this_month = datetime.today().strftime('%Y-%m')

    def open_spider(self,spider):
        self.to_exporter = {}
    def close_spider(self, spider):
        print("CLOSING SPIDER!!!")
        for f, exporter in self.to_exporter.values():
            exporter.finish_exporting()
            # 去除文件最後的逗號，並增加"]"
            f.seek(-1,2)
            f.truncate()
            f.write(b"]")
            f.close()
            # 壓縮成gz
            with open(f.name, 'rb') as f_in:
                with gzip.open(f'{f.name}.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.system(f'rm {f.name}')
        
    def process_item(self, item, spider):
        # Just for testing
        item['html'] = ''
        # End for testing
        # 儲存成json前，將xx_url存成str
        item['xx_url'] = str(item['xx_url'])
        # 文章不是這個月的才需要儲存
        published_month = item['published_date'][0:7]
        if published_month != self.this_month:
            f, exporter = self._exporter_for_item(item)
            exporter.export_item(item)
            f.write(b",")
        return item
    # 給定item，回傳對應的exporter
    def _exporter_for_item(self, item):
        published_date = item['published_date']
        created_at = item['created_at'].replace('-','').replace(' ','').replace(':','')
        y, m, d = published_date.split('-')
        website = item['website']
        folder_path = f'{const.LOCAL_FILE_HOME_DIR}/year={y}/month={m}'
        if (y,m,website) not in self.to_exporter:
            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)
            # create an exporter for the website
            file_path = folder_path+f'/{website}-{created_at}.json'
            f = open(file_path,'wb')
            f.write(b"[")
            exporter = JsonLinesItemExporter(f,encoding='utf-8',ensure_ascii=False)
            exporter.start_exporting()
            self.to_exporter[(y,m,website)] = f, exporter
        return self.to_exporter[(y,m,website)] 
 
class MysqlPipeline:
    today = datetime.today().strftime('%Y-%m-%d')
    def __init__(self):
        self.connect = pymysql.connect(
            host=const.MYSQL_HOST,
            db=const.MYSQL_DATABASE,
            user=const.MYSQL_USERNAME,
            passwd=const.MYSQL_PASSWORD,
            port=const.MYSQL_PORT,
            charset='utf8'
        )
        self.cursor = self.connect.cursor()
    def process_item(self, item, spider):
        if item['published_date'] != self.today:
            sql = 'INSERT INTO crawled_urls(xx_url, article_url, website, published_date, created_at) VALUES(%s,%s,%s,%s,%s)'
            data = (item['xx_url'], item['article_url'], item['website'], item['published_date'], item['created_at'])
            self.cursor.execute(sql, data)
        return item
    def close_spider(self, spider):
        self.connect.commit()
        self.connect.close()