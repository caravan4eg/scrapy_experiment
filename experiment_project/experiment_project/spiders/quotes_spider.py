"""
1. +++ Data extraction from http://quotes.toscrape.com/page
2. +++ Processing data to scrapy Item
3. +++ Processing data in pipeline: store it to PostgreSQL
4. Scrape proxies and make rquest to Quotes by proxy
5. Make User Agent rotation

"""

import scrapy
from ..items import QuotesItem


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]
    # location of saving to csv file
    # custom_settings = {
    #                     'FEED_URI': 'output/quotes_json.jl'
    #                 }

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
