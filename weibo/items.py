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

class UserInfoItem(scrapy.Item):
    onick = scrapy.Field()
    oid = scrapy.Field()
    page_id = scrapy.Field()
    realname = scrapy.Field()
    location = scrapy.Field()
    sex = scrapy.Field()
    sex_orient = scrapy.Field()
    relationship_status = scrapy.Field()
    birthday = scrapy.Field()
    blood = scrapy.Field()
    blog = scrapy.Field()
    infdomain = scrapy.Field()
    brief_introducation = scrapy.Field()
    register_time = scrapy.Field()
    email = scrapy.Field()
    qq = scrapy.Field()
    msn = scrapy.Field()
    company = scrapy.Field()
    highschool = scrapy.Field()
    college = scrapy.Field()
    tag = scrapy.Field()

    def get_insert_sql(self):
        # 执行具体插入
        insert_sql = """
            insert into user_info(onick, oid, page_id, realname, location, 
                                      sex, sex_orient, relationship_status, birthday, blood, blog,
                                      infdomain, brief_introducation, register_time, email, qq, msn,
                                      company, highschool, college, tag)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE onick = VALUES(onick), praise_nums = VALUES(praise_nums), 
            comment_nums = VALUES(comment_nums)
        """
        # ON DUPLICATE KEY UPDATE fav_nums = VALUES(fav_nums), praise_nums = VALUES(praise_nums), comment_nums = VALUES(comment_nums)

        params = (self['onick'], self['oid'], self['page_id'], self['realname'], self['location'],
                  self['sex'], self['sex_orient'], self['relationship_status'], self['birthday'], self['blood'],
                  self['blog'], self['infdomain'], self['brief_introducation'], self['register_time'], self['email'],
                  self['qq'], self['msn'], self['company'], self['highschool'], self['college'], self['tag'])

        return insert_sql, params
