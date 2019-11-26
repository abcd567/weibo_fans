# _*_ coding: utf-8 _*_
__author__ = "吴飞鸿"
__date__ = "2019/11/26 12:45"

import hashlib


def get_md5(url):
    m = hashlib.md5()
    # 不能用unicode编码
    try:
        url = url.encode("utf8")
    except:
        pass
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    print(get_md5("https://coding.imooc.com/lesson/92.html#mid=2878"))
