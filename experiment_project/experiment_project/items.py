import scrapy


class QuotesItem(scrapy.Item):
    """ Take in scraped data after yield in spider """
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()

