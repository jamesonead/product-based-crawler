import scrapy

from ..items import ArticleItem
from ..toolkits import tools

from datetime import datetime
import pytz

class PttSpider(scrapy.Spider):

    name = 'ptt'
    allowed_domains = ['www.ptt.cc']
    domain = 'https://www.ptt.cc'
    category = '汽車'
    count_page = 0

    # for first crawl
    first_crawl = False
    last_pg = 5
    # for first crawl

    # for update crawl
    max_page = 3
    # for update crawl

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.connect, self.cursor = tools.connect_mysql()

    def closed(self,reason):
        tools.close_mysql(self.connect,self.cursor)

    def start_requests(self):
        if self.first_crawl:
            #如果是第一次爬ptt，從第一頁(最早文章)開始爬
            for p in range(1,self.last_pg+1):
                yield scrapy.Request(url=f'https://www.ptt.cc/bbs/car/index{p}.html',
                            callback=self.get_every_articles)
        else:
            #如果是為了更新爬取新文章，從index頁(最新文章)開始爬取，爬完一頁再爬上一個目錄頁，直到沒有上一頁連結為止
            yield scrapy.Request(url='https://www.ptt.cc/bbs/car/index.html',
                                callback=self.get_every_articles)
            

    def get_every_articles(self, response):

        hrefs = response.xpath('//div[@class="title"]/a/@href').getall()
        urls = [self.domain + href for href in hrefs]
        not_crawled_urls = tools.not_crawled_urls(self.cursor,urls)
        print("not_crawled_urls=",not_crawled_urls)
        if len(not_crawled_urls)>0:
            for url,xx_url in not_crawled_urls:
                yield scrapy.Request(url=url, callback=self.parse)
        
        self.count_page = self.count_page + 1
        print(f'目前{self.name}已爬取{self.count_page}頁')

        # 如果不是第一次爬取ptt，且目前的目錄有爬取到新的文章，則抓取下一頁連結
        if (not self.first_crawl) and (len(not_crawled_urls) > 0):
            next_url = self.domain+response.xpath('//div[@class="btn-group btn-group-paging"]/a/@href').getall()[1]
            # 如果有下一頁連結，並且已經爬取過的目錄頁數目沒有超過max_page，則爬取下一頁
            print(f'next_url={next_url}')
            if next_url and (self.count_page < self.max_page):
                yield scrapy.Request(url=next_url,
                                callback=self.get_every_articles)

    def parse(self,response):
        timezone = pytz.timezone('Asia/Taipei')
        created_at = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        title = response.xpath('//div[@class="article-metaline"][2]/span[@class="article-meta-value"]/text()').get()
        time = response.xpath('//div[@class="article-metaline"][last()]/span[@class="article-meta-value"]/text()').get()
        published_date = datetime.strptime(time,'%a %b %d %H:%M:%S %Y').strftime('%Y-%m-%d')
        article_text = ''.join(response.xpath('//div[@id="main-content"]/text()').getall()).replace("\n","").replace("\r","")   
        data = {
            "website":self.name,
            "category":self.category,
            "title":title,
            "article_url":response.url,
            "xx_url":tools.hash_url(response.url),
            "created_at":created_at,
            "published_date":published_date,
            "article_text":article_text,
            "html":response.text
        }
        articleItem = ArticleItem(data)
        yield articleItem


