# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from pymongo.collection import Collection


# client = pymongo.MongoClient(host='127.0.0.1', port=27017)
# db = client['weibo']

class WeiboPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017, connect=False)
        db = self.client["weibo"]
        self.collection = db["python"]

    def process_item(self, item, spider):
        content = dict(item)
        self.collection.insert(content)
        print("###################已经存入MongoDB########################")
        return item

    def close_spider(self, spider):
        self.client.close()
        pass




