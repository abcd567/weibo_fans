# _*_ coding: utf-8 _*_
__author__ = "吴飞鸿"
__date__ = "2019/11/26 14:49"

import pymongo


class HandleMongo():
    def __init__(self, db, col):
        self.client = pymongo.MongoClient('localhost', 27017, connect=False)
        db = self.client[db]
        self.collection = db[col]

    def find(self, command, limit=20):
        # 查所有返回集合
        return self.collection.find(command).limit(limit)

    def update_one(self, condition, update):
        # 更新一条
        return self.collection.update_one(condition, update)

    def insert_one(self, document):
        self.collection.insert_one(document)

    def __del__(self):
        self.client.close()


if __name__ == '__main__':
    mon = HandleMongo('weibo', 'may_know')

    # results = mon.find({'done': True})
    # if results.count() == 0:
    #     print('空')
    # for r in results:
    #     print(r)
        # if r['username'] == '吴川爷爷':
        #     stat = mon.update_one({'username': r['username']}, {'$set': {'done': True}})
        #     print(stat)
        #     break

    # # 测试完毕，改回去
    results = mon.find({'done': True}, limit=100)
    print(results.count())
    # for r in results:
    #     print(r)
    while results.count():
        print(results.count())
        for r in results:
            stat = mon.update_one({'md5_index': r['md5_index']}, {'$set': {'done': False}})
            if stat.modified_count:
                print(">>>>>>>>>>>>>>>>修改成功")
        results = mon.find({'done': True}, limit=100)
    print('stop')
