# -*- coding: utf-8 -*-
import os

import pickle
from html import unescape

from lxml import etree

import scrapy
import time

from weibo.items import UserInfoItem
from weibo.secure import mycookie_dict
from weibo.utils.deal_date import date_format
from weibo.utils.handle_mongo import HandleMongo
from weibo.utils.js_2_xml_and_unescape import js2xml_unescape

client = HandleMongo('weibo', 'may_know')


class GetInfoSpider(scrapy.Spider):
    name = 'get_info'
    allowed_domains = ['weibo.com']
    start_urls = ['https://weibo.com']

    custom_settings = {
        "COOKIES_ENABLED": True,
        "COOKIES_DUBUG": True,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY ": 20,
        "DOWNLOAD_TIMEOUT": 15,
        "CONCURRENT_REQUESTS": 32,

        "ITEM_PIPELINES": {
            'weibo.pipelines.MysqlTwistedPipeline': 300,
        }
    }

    def start_requests(self):
        """
            直接引用cookie_dict,不再在此处模拟登陆
        """

        return [scrapy.Request(url=self.start_urls[0], cookies=mycookie_dict, dont_filter=True)]

    def parse(self, response):
        results = client.find({'done': False}, limit=10)

        if results.count() == 0:
            # 数据全部处理完了，spider close
            return
        for r in results:
            user_home = r['href']
            client.update_one({'md5_index': r['md5_index']}, {'$set': {'done': True}})
            yield scrapy.Request(url=user_home, callback=self.parse_detail)
        # 一轮数据循环结束,重新调用parse，这里访问的url无意义
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        script = response.xpath('//script/text()').extract()
        follow_count, fans_count, blog_count, onick, oid, page_id = '', '', '', '', '', ''
        for s in script:
            if 'FM.view({"ns":"","domid":"Pl_Core_T8CustomTriColumn__3"' in s:
                selector = js2xml_unescape(s)
                follow_count, fans_count, blog_count = self._selector_count(selector)

            if 'var $CONFIG = {};' in s:
                selector = js2xml_unescape(s)
                onick, oid, page_id = self._selector_id(selector)

            if follow_count and oid:
                break

        if follow_count and fans_count and blog_count and onick and oid and page_id:
            info_url = 'https://weibo.com/p/' + page_id + '/info?mod=pedit_more'
            params = {
                'onick': onick,
                'oid': int(oid),
                'page_id': int(page_id),
                'follow_count': int(follow_count),
                'fans_count': int(fans_count),
                'blog_count': int(blog_count)
            }
            # 这里要加上cookies, 大概是因为COOKIES_ENABLED不能
            yield scrapy.Request(url=info_url, meta=params, cookies=mycookie_dict, callback=self.handle_info)

    def handle_info(self, response):
        item = UserInfoItem()
        item['onick'] = response.meta.get('onick', '')
        item['oid'] = response.meta.get('oid', 0)
        item['page_id'] = response.meta.get('page_id', 0)
        item['follow_count'] = response.meta.get('follow_count', 0)
        item['fans_count'] = response.meta.get('fans_count', 0)
        item['blog_count'] = response.meta.get('blog_count', 0)

        script = response.xpath('//script/text()').extract()
        for s in script:
            if 'FM.view({"ns":"","domid":"Pl_Official_PersonalInfo__57"' in s:
                selector = js2xml_unescape(s)
                self._selector_info(selector, item)
                print(item)
                yield item

        time.sleep(10)

    @staticmethod
    def _selector_count(selector):
        follow_count = selector.xpath('//span[text()="关注"]/preceding-sibling::strong/text()')
        fans_count = selector.xpath('//span[text()="粉丝"]/preceding-sibling::strong/text()')
        blog_count = selector.xpath('//span[text()="微博"]/preceding-sibling::strong/text()')
        try:
            return follow_count.pop(), fans_count.pop(), blog_count.pop()
        except Exception as e:
            print('_selector_count()异常')
            print(e)

    @staticmethod
    def _selector_id(selector):
        onick = selector.xpath('//assign/left//string[text()="onick"]/ancestor::assign/right//string/text()')
        oid = selector.xpath('//assign/left//string[text()="oid"]/ancestor::assign/right//string/text()')
        page_id = selector.xpath('//assign/left//string[text()="page_id"]/ancestor::assign/right//string/text()')
        try:
            return onick.pop(), oid.pop(), page_id.pop()
        except Exception as e:
            print('_selector_id()异常')
            print(e)

    @staticmethod
    def _selector_info(selector, item):
        # 基本信息
        realname = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="真实姓名："]/following-sibling::span/text()')
        location = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="所在地："]/following-sibling::span/text()')
        sex = selector.xpath('//span[@class="pt_title S_txt2"][text()="性别："]/following-sibling::span/text()')
        sex_orient = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="性取向："]/following-sibling::span/text()')
        relationship_status = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="感情状况："]/following-sibling::span/text()')
        birthday = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="生日："]/following-sibling::span/text()')
        blood = selector.xpath('//span[@class="pt_title S_txt2"][text()="血型："]/following-sibling::span/text()')
        blog = selector.xpath('//span[@class="pt_title S_txt2"][text()="博客："]/following-sibling::a/text()')
        infdomain = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="个性域名："]/following-sibling::span/text()')
        brief_introducation = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="简介："]/following-sibling::span/text()')
        register_time = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="注册时间："]/following-sibling::span/text()')

        # 联系信息
        email = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="邮箱："]/following-sibling::span/text()')
        qq = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="QQ："]/following-sibling::span/text()')
        msn = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="MSN："]/following-sibling::span/text()')

        # 工作
        company_nodes = selector.xpath('//span[@class="pt_title S_txt2"][text()="公司："]/following-sibling::span')
        company = []
        for n in company_nodes:
            content = etree.tostring(n, pretty_print=True, encoding='utf8')
            txt = unescape(content.decode())
            s = etree.HTML(txt)
            company_name = s.xpath('//a/text()')
            work_detail = s.xpath('//span/text()')
            string = str(company_name.pop()) + ",".join([str(i) for i in work_detail])
            string = string.replace('\r\n', '').replace(' ', '')
            company.append(string)
        if company:
            company = " | ".join(company)
        else:
            company = ''

        # 高中
        highschool_nodes = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="高中："]/following-sibling::span')
        highschool = []
        for n in highschool_nodes:
            content = etree.tostring(n, pretty_print=True, encoding='utf8')
            s = etree.HTML(unescape(content.decode()))
            school_name = s.xpath('//a/text()')
            study_detail = s.xpath('//span/text()')
            string = str(school_name.pop()) + ",".join([str(i) for i in study_detail])
            string = string.replace('\r\n', '').replace(' ', '')
            highschool.append(string)
        if highschool:
            highschool = " | ".join(highschool)
        else:
            highschool = ''

        # 大学
        college_nodes = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="大学："]/following-sibling::span')
        college = []
        for n in college_nodes:
            content = etree.tostring(n, pretty_print=True, encoding='utf8')
            s = etree.HTML(unescape(content.decode()))
            college_name = s.xpath('//a/text()')
            study_meta = s.xpath('//span/text()')
            string = str(college_name.pop()) + ",".join([str(i) for i in study_meta])
            string = string.replace('\r\n', '').replace(' ', '')
            college.append(string)
        if college:
            college = " | ".join(college)
        else:
            college = ""

        # 标签
        tag_list = selector.xpath(
            '//span[@class="pt_title S_txt2"][text()="标签："]/following-sibling::span/a/text()')
        tag = []
        for t in tag_list:
            t = t.replace('\r\n', '').replace(' ', '')
            if t:
                tag.append(t)
        if tag:
            tag = ",".join(tag)
        else:
            tag = ""

        item['realname'] = "".join(realname)
        item['location'] = "".join(location)
        item['sex'] = "".join(sex)
        item['sex_orient'] = "".join(sex_orient).replace(' ', '').replace('\r\n', '')
        item['relationship_status'] = "".join(relationship_status).replace(' ', '').replace('\r\n', '')
        birthday = "".join(birthday)
        item['birthday'] = date_format(birthday)
        item['blood'] = "".join(blood)
        item['blog'] = "".join(blog)
        item['infdomain'] = "".join(infdomain)
        item['brief_introducation'] = "".join(brief_introducation)
        register_time = "".join(register_time).replace(' ', '').replace('\r\n', '')
        item['register_time'] = date_format(register_time)
        item['email'] = "".join(email)
        item['qq'] = "".join(qq)
        item['msn'] = "".join(msn)
        item['company'] = company
        item['highschool'] = highschool
        item['college'] = college
        item['tag'] = tag



