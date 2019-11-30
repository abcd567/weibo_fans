# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
import pymongo
# from pymongo.collection import Collection


# client = pymongo.MongoClient(host='127.0.0.1', port=27017)
# db = client['weibo']
from twisted.enterprise import adbapi


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


# 使用scrapy 提供的twisted异步框架完成数据插入关系型数据库
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        """创建连接池"""
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        """创建连接池"""
        # 从settings 里面提取值
        dbparms = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset="utf8mb4",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        # 上面dict内的参数名称要和 MySQLdb.connect()里的参数名称要一致
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        # 实例化自身
        return cls(dbpool)

    def process_item(self, item, spider):
        """调用连接池进行异步插入 是多线程"""
        # Interact with the database and return the result.
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体插入
        insert_sql, parmas = item.get_insert_sql()
        cursor.execute(insert_sql, parmas)

