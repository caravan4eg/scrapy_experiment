import json
import psycopg2
from scrapy.exceptions import DropItem
# from items import QuotesItem, ProxyItem

class QuotesJSONPipeline(object):
    """
    Process data that saved in items.QuotesItem container to JSON format
    Store data to CSV is processing automatically by tuning in settings and
    custom_settings in spider
    """

    def open_spider(self, spider):
        # Before write data into csv file purge it
        # self.file = open('output/quotes.csv', 'w').close()

        # JSON file purges itself before using
        self.file = open('output/quotes_json.jl', 'w')

    def process_item(self, item, spider):
        # Save data to json file

        # Print info to console for control and testing
        print('\n**************** QuotesJSONPipeline is running ***********')
        print(f'{str(item["author"]).upper()}: {str(item["tags"]).upper()}')
        print('************************************************************\n')

        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()


class QuotesDBPipeline(object):
    """
    Checks if item is there in db. If so then raises DropItem.
    Saves data saved  to PostgreSQL db
    """

    def open_spider(self, spider):
        # Make connection to PostgreSQL DB
        try:
            self.connection = psycopg2.connect(host='localhost',
                                               user='postgres',
                                               password='1',
                                               dbname='quotes')
            if self.connection:
                self.cur = self.connection.cursor()
                print('~~~~~~~~~~~~ Connected to database. OK! ~~~~~~~~~~~~\n', 
                        self.cur)
                # self.cur.execute('SELECT * FROM public.quotes_new_table')
                # recs = self.cur.fetchall()
                # print(recs)

            else:
                print("Cursor not found")

        except Exception as ex:
            print(ex)

    def process_item(self, item, spider):
        """ Checks and saves data to connected DB
            Note: item.save()  works ONLY with Django item and Djangomodels
            Use INSERT INTO
        """
        
        # check quote if already exists
        print('~~~~~~~~ Check if item already exists in db ~~~~~~~~~~~')
        
        # returns True or False
        # it didn't want to work because simply item[''].lower() is not a list 
        # and here have to be (item["author"].lower(),)
        self.cur.execute(
                        "select exists(\
                            SELECT author FROM public.quotes_new_table\
                            WHERE lower(author) = %s)", 
                        (item["author"].lower(),)   
                    )

        # returns ('True',) because of it man has to take 
        # "item_exists[0] == True" not simply "item_exists == True"
        item_exists = self.cur.fetchone()  
       
        if item_exists[0] == True:
            raise DropItem('Item already exists and won\'t be added to db')

        else:
            print('~~~~~~~~~~ Item will be added to db ~~~~~~~~~~~~~')
                       
            try:
                self.cur.execute("INSERT INTO public.quotes_new_table \
                                    (text, author, tags) VALUES (%s, %s, %s);",
                                 (item['text'],
                                  item['author'],
                                  item['tags']))
                spider.log('Item added to db. OK!')
            
            except Exception as ex:
                # Return back if is there a problem with saving
                self.cur.execute("rollback")
                print('~~~~~ Something went wrong with saving to DB!!! ~~~~~')
                print(ex)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        self.connection.commit()
        return item

    def close_spider(self, spider):
        # close connection to DB
        self.cur.close()
        self.connection.close()


class ProxyPipeline(object):
    
    def open_spider(self, spider):
        # Purge old or create new file with list of proxies
        try:
            self.file = open('output/list.txt', 'w').close()
            print('~~~~~~~~~~~~ Old proxy list deleted successfully. OK ~~~~~~~~~~~~')
    
        except:
            print('~~~~~~~~~~~~ Skeep delet of old file... ~~~~~~~~~~~~')
    
        # open new proxy list
        self.file = open('output/list.txt', 'a')

    def process_item(self, item, spider):
        # write down new proxy to list.txt
        self.file.write('http://' + item['ip'] + ':' + item['port'] + '\n')
        spider.log('<<<<< ProxyPipeline >>>>>: processed new proxy url to list.txt...')
        return item

    def close_spider(self, spider):
        self.file.close()