# _*_ coding: utf-8 _*_
__author__ = "吴飞鸿"
__date__ = "2019/11/26 13:57"

import re


def get_follow_page(response):
    patt = re.compile(r'<a bpfilter=\\"page_frame\\".*?href=\\"(.*?)\\" >.*?<span.*?关注<\\/span>')
    url_list = patt.findall(response.text)
    try:
        return url_list[0].replace('\\/', '/').replace('//', 'https://')
    except Exception as e:
        print(e)
