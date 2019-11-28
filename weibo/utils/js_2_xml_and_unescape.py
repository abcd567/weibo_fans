# _*_ coding: utf-8 _*_
__author__ = "吴飞鸿"
__date__ = "2019/11/28 0:31"
from html import unescape

from lxml import etree

import js2xml


def js2xml_unescape(script_text, encoding='utf8', debug=False):
    """
    :param script_text:
    :param encoding:
    :param debug:
    :return: selector
    """
    tree = js2xml.parse(script_text, encoding=encoding, debug=debug)
    script_tree = js2xml.pretty_print(tree)
    # 字符反转义
    script_tree = unescape(script_tree)
    selector = etree.HTML(script_tree)
    return selector
    # name = script_selector.xpath('//li[@class="follow_item S_line2"]//dt/a/@title')
    # for n in name:
    #     print(n)
