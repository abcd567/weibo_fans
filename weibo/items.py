# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    # define the fields for your item here like:
    username = scrapy.Field()
    href = scrapy.Field()
    md5_index = scrapy.Field()
    done = scrapy.Field()
    pass


class WeiboRealUserItem(scrapy.Item):
    # define the fields for your item here like:
    username = scrapy.Field()
    href = scrapy.Field()
    md5_index = scrapy.Field()
    done = scrapy.Field()
    follow_count = scrapy.Field()
    fans_count = scrapy.Field()
    article_count = scrapy.Field()
    pass
