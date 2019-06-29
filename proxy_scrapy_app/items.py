import scrapy


class TendersItem(scrapy.Item):
    print('\n**** <TendersItem>: we are here\n')
    number = scrapy.Field()
    customer = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
    deadline = scrapy.Field()
    country = scrapy.Field()
    url_addr = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()