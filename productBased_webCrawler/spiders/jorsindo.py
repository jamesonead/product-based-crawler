import scrapy
from bs4 import BeautifulSoup

from datetime import datetime
import pytz

from ..items import ArticleItem
from ..toolkits import tools
import re

class JorsindoSpider(scrapy.Spider):

    name = 'jorsindo'
    allowed_domains = ['forum.jorsindo.com']
    domain = 'https://forum.jorsindo.com/'

    count_page = {49:0,116:0,114:0,115:0,119:0}

    first_crawl = False
    # for first and update crawl
    max_page = 2
    # for first and update crawl


    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.connect, self.cursor = tools.connect_mysql()

    def closed(self,reason):
        tools.close_mysql(self.connect,self.cursor)

    def start_requests(self):
        cat_ids = [cat_id for cat_id in self.count_page]
        # first_pages:所有文章類型下的第一頁目錄
        first_pages = ['https://forum.jorsindo.com/forum-{}-1.html'.format(id) for id in cat_ids]

        for cat_id, first_page in zip(cat_ids,first_pages):
            if self.first_crawl:
                # 第一次跑
                yield scrapy.Request(url=first_page, callback=self.get_last_page,
                                    meta={"cat_id":cat_id})
            else:
                # 跑更新程式
                yield scrapy.Request(url=first_page, callback=self.get_every_articles,
                                    meta={"cat_id":cat_id})

    # 只有第一次爬蟲會需要用到
    # jorsindo最舊的文章會在最後一頁，此函式會由最舊的目錄頁面開始爬取文章
    def get_last_page(self,response):
        cat_id = response.meta['cat_id']
        last_pg_url = response.xpath('//div[@class="pg"]/a[@class="last"]/@href').get()
        x = re.findall(r"(\d+).html",last_pg_url) # x is a list
        last_pg = int(x[0]) if len(x) > 0 else 0
        if last_pg > 0:
            for p in range(last_pg,0,-1):
                url = f'https://forum.jorsindo.com/forum-{cat_id}-{p}.html'
                print(url)
                yield scrapy.Request(url=url, callback=self.get_every_articles,
                                    meta={"cat_id":cat_id},dont_filter=True)
        else:
            print('[ERROR] Cannot find the last page.')

    def get_every_articles(self,response):

        cat_id = response.meta['cat_id']

        hrefs = response.xpath('//table[@id="threadlisttableid"]/tbody[contains(@id,"normalthread_")]//a[@class="s xst"]/@href').getall()
        urls = [self.domain + href for href in hrefs]
        not_crawled_urls = tools.not_crawled_urls(self.cursor,urls)
        #print(not_crawled_urls)
        if len(not_crawled_urls)>0:
            for url,xx_url in not_crawled_urls:
                yield scrapy.Request(url=url, callback=self.parse)

        self.count_page[cat_id] = self.count_page[cat_id] + 1
        print(f'目前{self.name}:{cat_id}已爬取{self.count_page[cat_id]}頁')

        # 如果不是第一次爬jorsindo，則爬取下一頁目錄
        if (not self.first_crawl) and len(not_crawled_urls)>0:
            # 獲取前一頁目錄的url
            next_url = self.domain+response.xpath('//div[@class="pg"]/a[@class="nxt"]/@href').get()
            if next_url and (self.count_page[cat_id]<self.max_page):
                yield scrapy.Request(url=next_url, callback=self.get_every_articles,meta={"cat_id":cat_id})
        

    def parse(self, response):
        timezone = pytz.timezone('Asia/Taipei')

        created_at = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        published_date = response.xpath('//div[@class="authi firstauthi"]/em/text()').get().split(" ")[0]
        # 小老婆文章的發布日期格式為, ex: 2022-5-5，為了統一格式，將其轉換成 2022-05-05
        published_date = datetime.strftime(datetime.strptime(published_date,'%Y-%m-%d'),'%Y-%m-%d')

        title = response.xpath('//span[@id="thread_subject"]/text()').get()
        article_url = response.url
        xx_url = tools.hash_url(response.url)
        html = response.text
        # 獲取文章類別
        category_bar = response.xpath('//div[@id="pt"]/div/a/text()').getall()
        cat = category_bar[1]
        sub_cat = category_bar[2].replace('/','')
        category = f'{cat}/{sub_cat}'
        # 解析文章全文
        content = response.xpath('//td[@class="t_f"]').get()
        soup = BeautifulSoup(content,'lxml')
        drop_elements = ['ignore_js_op','iframe']
        for drop_element in drop_elements:
            for ele in soup.find_all(drop_element):
                ele.decompose()
        pstatus = soup.find("i", class_="pstatus")
        if pstatus:
            pstatus.decompose()
        article_text = soup.getText().replace("\n","").replace("\r","")

        data = {
            "website":self.name,
            "category":category,
            "title":title,
            "article_url":article_url,
            "xx_url":xx_url,
            "created_at":created_at,
            "published_date":published_date,
            "article_text":article_text,
            "html":html
        }
        print(data)
        articleItem = ArticleItem(data)
        yield articleItem
        
        
        
