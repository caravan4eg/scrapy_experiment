import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.utils.project import get_project_settings
from datetime import date
# from .items import TendersItem
from time import sleep
import random
from random import randint
# import urllib.request

RESULT_PAGE_PRIORITY = 0
PRODUCT_PAGE_PRIORITY = 100

# -----------------------------
"""Pipline
Save to db?????
scrapy_launcher.py
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import csv

# ---------------------------------
'''Per request delay'''
class PerRequestDelaySlot(Slot):
    def download_delay(self):
        if self.queue:
            if "per_request_delay" in self.queue[0][0].meta.keys():
                print("PER_REQUEST_DELAY:" +str(self.queue[0][0].meta["per_request_delay"]))
                return self.queue[0][0].meta["per_request_delay"]
        #from original:
        if self.randomize_delay: #
            return random.uniform(0.5 * self.delay, 1.5 * self.delay)
        return self.delay



# =============================

# define a spider
class IceSpiderSpider(scrapy.Spider):
    name = "ice_spider"
    today_is = date.today().strftime("%d.%m.%Y")
    custom_settings = {
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY': 10,  # per download slot value -> per proxy value
        'CONCURRENT_REQUESTS': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'FEED_FORMAT': 'csv',
        'FEED_URI': f'output/{today_is}_icetrade_tenders.csv',
                }

    proxies = {}

    # def check_request_params(self, url, headers, meta):
    #     request = urllib.request.Request(url, headers, meta)
    #     response = urllib.request.urlopen(request)
    #     html = response.read()
    #
    #     print(f'Request sent >>>>>>>>>>>\n {url} \n {headers} \n {meta}')
    #     print(f'Response recevied by HTTPBin >>>>>>>>>>>>\n {html}')
    #     print("-------------------\n\n")

    def get_proxy_meta(self):
        meta =  {}
        proxy = min(self.proxies, key=self.proxies.get)
        self.proxies[proxy] += 1
        meta['download_slot'] = proxy
        print('\n>>>>>>>>>>>>>>>>>>>>>>>> Meta, Proxy: ', meta)
        # meta["cookie_jar"] = proxy
        return meta

    # def get_ua_header(self):
    #     user_agent_list = [
    #
    #     ]
    #     # Pick a random user agent
    #     user_agent = random.choice(user_agent_list)
    #     # Set the headers
    #     headers = {'User-Agent': user_agent}
    #     return headers

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(IceSpiderSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def start_requests(self):
        yield scrapy.Request(url="http://free-proxy-list.net/",
                             callback=self.parse_proxy)
        self.crawler.stats._stats["used_proxies"] = self.proxies

    def spider_closed(self, spider):
        self.crawler.stats._stats["used_proxies_count"] = len(list(self.proxies))

    def parse_proxy(self, response):
        for row in response.xpath('//table/tbody/tr'):
            # item = ProxyItem()
            row_data = row.xpath('.//td/text()').getall()
            # item['ip'] = row.xpath('.//td/text()')[0].get()
            # item['port'] = row.xpath('.//td/text()')[1].get()

            if 'elite proxy' in row_data: #
                host_port = row_data[0]+':'+row_data[1]
                self.proxies[host_port] = 0
                self.logger.info('\n**** <parse_proxy>: extracted proxy <%s>:\n' % host_port)
                print(row_data[0], row_data[1])

        if len(list(self.proxies)) > 0:
            self.logger.info('\n**** Well, we are going to scrape Icetrade after extract proxies...\n')

            yield scrapy.Request(url='http://www.icetrade.by/search/auctions?search_text=&search=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&zakup_type[1]=1&zakup_type[2]=1&auc_num=&okrb=&company_title=&establishment=0&period=&created_from=&created_to=&request_end_from=&request_end_to=&t[Trade]=1&t[eTrade]=1&t[Request]=1&t[singleSource]=1&t[Auction]=1&t[Other]=1&t[contractingTrades]=1&t[socialOrder]=1&t[negotiations]=1&r[1]=1&r[2]=2&r[7]=7&r[3]=3&r[4]=4&r[6]=6&r[5]=5&sort=num%3Adesc&onPage=100&p=1',
                                meta=self.get_proxy_meta(),
                                callback=self.parse,
                                priority=PRODUCT_PAGE_PRIORITY,
                                #errback=self.err_back,
                                # headers=self.get_ua_header(),
                            )

    def parse(self, response):
        """ Get page url """
        sleep(randint(3, 8))
        self.logger.info('\n**** <parse>: we are going to scrape Icetrade page...\n')
        last_page = response.xpath('//div[@id="content"]/div[@class="paging"]/a[9]/text()').get().strip()

        # for i in range(3):  # scrape some pages for test, not all
        for i in range(int(last_page)+1):
            sleep(randint(3, 5))

            self.logger.info('\n**** <parse>: processing page: <%s>:\n' % str(i))

            yield scrapy.Request(f'http://www.icetrade.by/search/auctions?search_text=&search=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&zakup_type[1]=1&zakup_type[2]=1&auc_num=&okrb=&company_title=&establishment=0&period=&created_from=&created_to=&request_end_from=&request_end_to=&t[Trade]=1&t[eTrade]=1&t[Request]=1&t[singleSource]=1&t[Auction]=1&t[Other]=1&t[contractingTrades]=1&t[socialOrder]=1&t[negotiations]=1&r[1]=1&r[2]=2&r[7]=7&r[3]=3&r[4]=4&r[6]=6&r[5]=5&sort=num%3Adesc&onPage=100&p={str(i)}',
                                   meta=self.get_proxy_meta(),
                                   callback=self.parse_page,
                                   priority=RESULT_PAGE_PRIORITY)


    def parse_page(self, response):
        """ Extract tender information """
        sleep(randint(1, 5))
        item = {}
        for line in response.xpath('//*/tr[contains(@class, "rw")]'):
            # item = TendersItem()
            item['number'] = line.xpath('.//td[4]/text()').get().strip()
            item['customer'] = line.xpath('.//td[2]/text()').get().strip()
            item['description'] = line.xpath('.//td[1]/a/text()').get().strip()
            item['price'] = line.xpath('.//td[5]/span/text()').get().strip()
            item['country'] = line.xpath('.//td[3]/text()').get().strip()
            item['url_addr'] = line.xpath('.//td[1]/a/@href').get()
            # change date format dd-mm-yyyy --> yyyy-mm-dd
            ddmmyyyy = line.xpath('.//td[6]/text()').get().strip()
            yyyymmdd = ddmmyyyy[6:] + "-" + ddmmyyyy[3:5] + "-" + ddmmyyyy[:2]
            item['deadline'] = yyyymmdd

            self.logger.info('\n**** <parse_page>: scrapping tender <%s>:' % item['number'])
            yield item

    def err_back(self, failure):
        #Not finished/tested yet
        req = failure.request
        if "download_slot" in req.meta.keys():
            failed_proxy = req.meta["download_slot"]
            if failed_proxy in self.proxies.keys():
                del self.proxies[failed_proxy] #delete not valid proxy
                req.meta = self.get_proxy_meta() # get new proxy
                yield req

process = CrawlerProcess(get_project_settings())
process.crawl(IceSpiderSpider)
process.start()