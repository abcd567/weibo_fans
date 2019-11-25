# _*_ coding: utf-8 _*_
__author__ = "吴飞鸿"
__date__ = "2019/5/23 22:21"

import sys
import os

from scrapy.cmdline import execute

# 添加工作路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(["scrapy", "crawl", "weibo_user"])