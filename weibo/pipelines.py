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
        self.collection = db["users_homepage"]
        self.collection.create_index([("md5_index", 1)], unique=True)

    def process_item(self, item, spider):
        content = dict(item)
        try:
            self.collection.insert(content)
        except Exception as e:
            print("++++++++++++++++++++++重复数据+++++++++++++++++++++++++++")
            return item
        print("###################已经存入MongoDB########################")
        return item

    def close_spider(self, spider):
        self.client.close()
        pass


class NewWeiboPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017, connect=False)
        db = self.client["weibo"]
        self.collection = db["real_user"]
        self.collection.create_index([("md5_index", 1)], unique=True)

    def process_item(self, item, spider):
        content = dict(item)
        try:
            self.collection.insert(content)
        except Exception as e:
            print("++++++++++++++++++++++重复数据+++++++++++++++++++++++++++")
            return item
        print("###################已经存入MongoDB########################")
        return item

    def close_spider(self, spider):
        self.client.close()
        pass

