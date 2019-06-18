from .items import QuotesItem
import json


class QuotesPipeline(object):
    """ Process data that saved in items.QuotesItem container """

    def open_spider(self, spider):
        '''Open json and csv files for writing data
        '''

        # Before write data into csv file purge it
        self.file = open('output/quotes.csv', 'w').close()

        # JSON file purges before using themself
        self.file = open('output/quotes_json.jl', 'w')

    def process_item(self, item, spider):
        '''Save data to json file
        '''
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)

        # Print info to console for control and testing
        print('\n**************** QuotesPipeline is running ****************')
        print(f'{str(item["author"]).upper()}: {str(item["tags"]).upper()}')
        print('************************************************************\n')

        def close_spider(self, spider):
            self.file.close()

        return item
