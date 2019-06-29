# define a pipeline
class CsvWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.csv', 'w',encoding="utf8")
        self.csvwriter = csv.writer(self.file)
        self.csvwriter.writerow(["Author", "Quote", "Tags"]) #Custom header

    def process_item(self,item,spider):
        row = [item["author"],item["quote"],",".join(item["tags"])]
        self.csvwriter.writerow(row)
        return item

    def close_spider(self,spider):
        self.file.close()