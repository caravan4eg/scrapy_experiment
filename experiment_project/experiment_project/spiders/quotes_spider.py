"""
1. +++ Data extraction from http://quotes.toscrape.com/page
2. +++ Processing data to scrapy Item
3. +++ Processing data in pipeline: check if exists and 
       store it to PostgreSQL
4. +++ Scrape proxies and make request to Quotes with proxy
5. +++ Make User Agent rotation

"""

import scrapy
from ..items import QuotesItem

from scrapy import signals

RESULT_PAGE_PRIORITY = 0
PRODUCT_PAGE_PRIORITY = 100


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    custom_settings = {
                    'COOKIES_ENABLED': False,
                    'DOWNLOAD_DELAY': 5,  # per download slot value -> per proxy value
                    'CONCURRENT_REQUESTS': 3,
                    'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
                        }

    proxies = {}

    def get_proxy_meta(self):
        meta =  {}
        proxy = min(self.proxies, key=self.proxies.get)
        self.proxies[proxy] += 1
        meta['download_slot'] = proxy
        # meta["cookie_jar"] = proxy
        return meta

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(QuotesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def start_requests(self):
        yield scrapy.Request(url="https://www.us-proxy.org/",
                             callback=self.parse_proxy)
        self.crawler.stats._stats["used_proxies"] = self.proxies

    def spider_closed(self, spider):
        self.crawler.stats._stats["used_proxies_count"] = len(list(self.proxies))
        print('~~~~~~~~~~~~ Spider "%s" closed ~~~~~~~~~~' % spider.name)

    def parse_proxy(self, response):
        print('~~~~~~~~~~~~ Getting proxy list ~~~~~~~~~~')
        for row in response.xpath('//table/tbody/tr'):
            # proxy_item = ProxyItem()
            row_data = row.xpath('.//td/text()').getall()
            # proxy_item['ip'] = row.xpath('.//td/text()')[0].get()
            # proxy_item['port'] = row.xpath('.//td/text()')[1].get()
            
            # Use it in case too few elite proxy
            # host_port = row_data[0]+':'+row_data[1]
            # self.proxies[host_port] = 0
            # print(f'~~~~~~~~~~~~ Proxy URL: {host_port}  ~~~~~~~~~~')

            if 'elite proxy' in row_data: #
                host_port = row_data[0]+':'+row_data[1]
                self.proxies[host_port] = 0
                print(f'~~~~~~~~~~~~ Proxy URL: {host_port}  ~~~~~~~~~~')

                

        if len(list(self.proxies)) > 0:
            yield scrapy.Request(url='http://quotes.toscrape.com/page/1/',
                                 meta=self.get_proxy_meta(),
                                 callback=self.parse,
                                 priority=PRODUCT_PAGE_PRIORITY,
                                 # errback=self.err_back,
                                 # headers=self.get_ua_header(),
                            )

        print(f'~~~~~~~~~~~~ Proxy list ready. Proxies total: \
              {len(self.proxies)}  ~~~~~~~~~~')

    def parse(self, response):
        """
        Extract data and transfer them to item container
        """
        print('Response.meta', response.meta)

        for quote in response.css('div.quote'):
            item = QuotesItem()
            item['text'] = quote.css('span.text::text').get()
            item['author'] = quote.css('small.author::text').get()
            item['tags'] = quote.css('div.tags a.tag::text').getall()

            yield item


    def err_back(self, failure):
        # Not finished/tested yet
        req = failure.request
        if "download_slot" in req.meta.keys():
            failed_proxy = req.meta["download_slot"]
            if failed_proxy in self.proxies.keys():
                del self.proxies[failed_proxy]  # delete not valid proxy
                req.meta = self.get_proxy_meta()  # get new proxy
                yield req