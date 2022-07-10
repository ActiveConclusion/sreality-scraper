import scrapy


class SrealitySpider(scrapy.Spider):
    name = 'sreality'
    allowed_domains = ['sreality.cz']
    start_urls = ['http://sreality.cz/']

    def parse(self, response):
        pass
