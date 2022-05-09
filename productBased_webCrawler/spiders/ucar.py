import scrapy
from ..toolkits import tools
from ..items import ArticleItem

import scrapy
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

class UcarSpider(scrapy.Spider):
    name = "ucar"
    domain = 'https://forum.u-car.com.tw'
    categories = {1:{'name':'汽車'}}
    # just for test
    count = 0
    max = 2
    # end for test
    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.connect, self.cursor = tools.connect_mysql()

    def closed(self,reason):
        tools.close_mysql(self.connect,self.cursor)

    def start_requests(self):
        for cat_id in self.categories:
            first_pg = f'https://forum.u-car.com.tw/forum/list?category={cat_id}'
            yield scrapy.Request(url=first_pg, callback=self.get_every_page_article)

    def get_every_page_article(self,response):
        # just for test
        self.count = self.count + 1
        if self.count > self.max:
            return
        # end for test
        print("ucar crawling page {}".format(self.count))
        hrefs = response.xpath('//div[@class="title "]/a/@href').getall()
        urls = [self.domain+href for href in hrefs]
        not_crawled_urls = tools.not_crawled_urls(self.cursor,urls)
        #print("not_crawled_urls=",not_crawled_urls)
        if not_crawled_urls:
            for url,xx_url in not_crawled_urls:
                yield scrapy.Request(url=url, callback=self.parse)
            next_url = self.domain+response.xpath('//li[@class="arrow_right_s"]/a[@class="arrow_right_1"]/@href').get()
            if next_url:
                yield scrapy.Request(url=next_url, callback=self.get_every_page_article)
        
    
    def parse(self, response):
        timezone = pytz.timezone('Asia/Taipei')
        created_at = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        category = '/'.join(response.xpath('//div[@id="forum_jumper"]/ul/li/a/text()').getall())
        content = response.xpath('//div[@class="forum_list_area"]').get()
        soup = BeautifulSoup(content,'lxml')
        title = soup.find("div",class_="cell_post_title").text
        published_date = soup.find("div",class_="user_group").find_all("p")[1].text.split(" ")[0].replace("/","-")
        article_text = soup.find("div",class_="cell_post_area").find("div",class_="comment").text.replace("\n","").replace("\r","").replace("\xa0","")
        data = {
            "website":self.name,
            "category":category,
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
