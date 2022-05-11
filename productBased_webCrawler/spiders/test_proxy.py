import scrapy


class TestProxySpider(scrapy.Spider):
    name = 'test_proxy'
    proxy = {'proxy':'http://61.216.156.222:60808'}
    def start_requests(self):
        first_page = 'https://httpbin.org/ip'
        yield scrapy.Request(url=first_page, callback=self.parse,
                                    meta=self.proxy)

    def parse(self, response):
        print(response.text)
        pass
