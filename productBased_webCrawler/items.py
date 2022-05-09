# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ArticleItem(scrapy.Item):
    website = scrapy.Field()
    category = scrapy.Field()
    created_at = scrapy.Field()
    published_date = scrapy.Field()
    title = scrapy.Field()
    article_url = scrapy.Field()
    xx_url = scrapy.Field()
    article_text = scrapy.Field()
    html = scrapy.Field()


