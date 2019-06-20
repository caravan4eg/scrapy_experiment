import json
import psycopg2

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
        print('\n**************** QuotesJSONPipeline is running ****************')
        print(f'{str(item["author"]).upper()}: {str(item["tags"]).upper()}')
        print('************************************************************\n')

        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()


class QuotesDBPipeline(object):
    """
    Process data saved in items.QuotesItem container
    to PostgreSQL DB
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
                print('***************** Connected to database. OK! ***************\n', self.cur)
                self.cur.execute('SELECT * FROM public.quotes_new_table')

                recs = self.cur.fetchall()
                print(recs)

            else:
                print("Cursor not found")

        except Exception as ex:
            print(ex)


    def process_item(self, item, spider):
        # Save data to connected DB
        print('\n**************** QuotesDBPipeline is processing scraped data to database ****************')
        print(f'{str(item["author"]).upper()}: {str(item["tags"]).upper()}')
        print('************************************************************\n')

        try:
            self.cur.execute('''
                             insert into public.quotes_new_table (text, author, tags) 
                             values (%s, %s, %s);''',
                             (item['text'],
                              item['author'],
                              item['tags']))
        except:
            self.cur.execute("rollback")

        self.connection.commit()
        return item

    def close_spider(self, spider):
        # close connection to DB
        self.cur.close()
        self.connection.close()


