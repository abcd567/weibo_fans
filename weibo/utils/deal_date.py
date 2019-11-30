# _*_ coding: utf-8 _*_
from datetime import date

__author__ = "吴飞鸿"
__date__ = "2019/11/30 0:46"

import re


def date_format(date_str):
    if '月' in date_str:
        if '年' in date_str:
            r = re.match(r'(\d+)年(\d+)月(\d+)日', date_str)
            year = r.group(1)
            month = r.group(2)
            day = r.group(3)
            return date(year=int(year), month=int(month), day=int(day))
        else:
            r = re.match(r'(\d+)月(\d+)日', date_str)
            month = r.group(1)
            day = r.group(2)
            return date(year=8888, month=int(month), day=int(day))

    elif '-' in date_str:
        r = re.match(r'(\d+)-(\d+)-(\d+)', date_str)
        year = r.group(1)
        month = r.group(2)
        day = r.group(3)
        return date(year=int(year), month=int(month), day=int(day))
    else:
        pass


if __name__ == '__main__':
    a = '5月9日'
    b = '1888年5月18日'
    c = '2011-04-20'
    # date_format(a)
    result = map(date_format, [a, b, c])
    for r in result:
        print(r)
    print()

