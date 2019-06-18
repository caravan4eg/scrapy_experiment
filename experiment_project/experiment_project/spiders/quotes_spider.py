import scrapy
from ..items import QuotesItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]
    # location of saving to csv file
    custom_settings = {
                        'FEED_URI': 'output/quotes.csv'
                    }

    def parse(self, response):
        """
        Extract data and transfer them to item container
        """

        for quote in response.css('div.quote'):
            item = QuotesItem()
            item['text'] = quote.css('span.text::text').get()
            item['author'] = quote.css('small.author::text').get()
            item['tags'] = quote.css('div.tags a.tag::text').getall()

            yield item
