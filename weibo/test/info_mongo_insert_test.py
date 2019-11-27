# _*_ coding: utf-8 _*_
from weibo.utils.handle_mongo import HandleMongo

__author__ = "吴飞鸿"
__date__ = "2019/11/27 19:44"


if __name__ == '__main__':
    connect = HandleMongo('weibo', 'info')
    test_data = {'nick': '四等南人', 'local': '广东', 'sex': '男', 'sexual_orientation': '异性恋', 'birthday': '1994年12月25日',
                 'introduce': '哈哈哈哈哈哈哈'}
    test_data_2 = {'nick': '四等南人', 'local': '广东', 'sex': '男', 'sexual_orientation': '异性恋', 'birthday': '1994年12月25日',
                   'introduce': '哈哈哈哈哈哈哈', 'register_time': '2012-01-01'}
    connect.insert_one(test_data)
    connect.insert_one(test_data_2)
    print('>>>>>>>>>>>>>>>>>>>>>>>OK')
    # 改用mysql吧，结构太乱了
