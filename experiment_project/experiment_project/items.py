import scrapy


class QuotesItem(scrapy.Item):
    """ Scraped data is stored here after yield in spider """
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()

class ProxyItem(scrapy.Item):
    ip = scrapy.Field()
    port = scrapy.Field()