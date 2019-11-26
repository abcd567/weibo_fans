# -*- coding: utf-8 -*-
import pickle

import os

import re
import scrapy
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from weibo.items import WeiboItem
from weibo.secure import weibo_account, weibo_password
from weibo.settings import project_dir
from weibo.utils.handle_mongo import HandleMongo
from weibo.utils.to_md5 import get_md5


client = HandleMongo('weibo', 'users_homepage')


class U2FollowSpider(scrapy.Spider):
    name = 'u_2_follow'
    allowed_domains = ['weibo.com']
    start_urls = ['https://weibo.com']

    custom_settings = {
        "COOKIES_ENABLED": True,
        "COOKIES_DUBUG": True,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 3,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        "AUTOTHROTTLE_TARGET_CONCURRENCY ": 10,
        "DOWNLOAD_TIMEOUT": 15,

        "ITEM_PIPELINES": {
            'weibo.pipelines.NewWeiboPipeline': 300,
        }
    }
    count = 1


    def start_requests(self):
        """
            判断本地是否存在cookies，存在直接使用cookies登陆,否则selenium模拟登陆
        """
        cookies = []
        if os.path.exists(project_dir + "/cookies/weibo.cookie"):
            cookies = pickle.load(open(project_dir + "/cookies/weibo.cookie", "rb"))

        if not cookies:
            # 登陆获取cookies
            option = webdriver.ChromeOptions()
            option.add_experimental_option('excludeSwitches', ['enable-automation'])
            browser = webdriver.Chrome(executable_path='I:\\谷歌下载\\chromedriver_win32\\chromedriver.exe', options=option)
            try:
                browser.maximize_window()
                browser.implicitly_wait(5)
            except:
                pass
            browser.get("https://www.weibo.com")
            if WebDriverWait(browser, 20).until(lambda x: x.find_element_by_xpath('//a[@node-type="loginBtn"]')):
                browser.implicitly_wait(10)
                browser.find_element_by_id('loginname').clear()
                browser.find_element_by_xpath('//input[@id="loginname"]').send_keys(weibo_account)
                browser.implicitly_wait(1)
                browser.find_element_by_xpath('//input[@type="password"]').send_keys(weibo_password)
                browser.implicitly_wait(10)
                time.sleep(10)
                # 如果验证码，在下一行加入处理逻辑
                browser.find_element_by_css_selector('a.W_btn_a.btn_32px').click()
                time.sleep(10)

                # 如果使用无头浏览器headless，可选择开启可视化
                # browser.get_screenshot_as_file('screenshot/weibo_homepage.jpg')
                # txt = browser.page_source
                # with open('html_file/weibo_homepage.html', 'wb') as f:
                #     f.write(txt.encode(encoding='utf8'))

                # 登陆成功，获取cookie，并保存
                cookies = browser.get_cookies()
                pickle.dump(cookies, open(os.path.join(project_dir, 'cookies\\weibo.cookie'), "wb"))

        # 加载cookies,并使用cookies访问起始url
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        return [scrapy.Request(url=self.start_urls[0], cookies=cookie_dict, dont_filter=True)]

    def parse(self, response):
        if response.status == 200:
            results = client.find({'done': False}, limit=2)
            if results.count() == 0:
                # 数据全部处理完了，spider close
                return
            for r in results:
                user_home = r['href']
                client.update_one({'href': user_home}, {'$set': {'done': True}})
                yield scrapy.Request(url=user_home, callback=self.handle_user_home)
            # 一轮数据循环结束,重新调用parse，这里访问的url无意义
            yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    @staticmethod
    def _get_follow_page(text):
        # url_list = re.findall(r'<a bpfilter=\\"page_frame\\".*?href=\\"(.*?)\\" >.*?<span.*?关注<\\/span>', text)
        # 曾经运行上行注释代码会出现偶尔会出现在这里卡死的情况
        # 正则: r'<a bpfilter=\\"page_frame\\".*?href=\\"(.*?)\\" >.*?<span.*?关注<\\/span>'
        # 原因猜测：正则缓存问题 or 匹配算法复杂度指数上升
        # 卡死处执行了 re.py > _compile()代码： 290~291行
        # p, loc = _cache[type(pattern), pattern, flags]
        # if loc is None or loc == _locale.setlocale(_locale.LC_CTYPE):
        #     return p

        url_list = re.findall(r'href=\\"(.*?)\\" ><strong.*?关注', text)

        try:
            return url_list[0].replace('\\/', '/').replace('//', 'https://')
        except Exception as e:
            print(e)

    def handle_user_home(self, response):
        if response.status == 200:
            follow_page = self._get_follow_page(response.text)
            # 这里先不提取个人信息，待数据量足够多，再写另一个爬虫提取信息
            yield scrapy.Request(url=follow_page, callback=self.get_user)

    def _get_next_page(self, text):
        # 由于被系统限制，每个账号只能查看5页粉丝
        if self.count <= 5:
            self.count += 1
            href = re.findall(r'page next.*?href=\\"(.*?)\\"', text)
            if href:
                href = href[0].replace('\\/', '/')
                next_url = 'https://weibo.com' + href
                return next_url
            # 没有下一页返回0

        # 5轮重置count
        if self.count > 5:
            self.count = 1

        # 只要没有下一页就返回false,不管满不满5页
        return False

    def get_user(self, response):
        if response.status == 200:
            text = response.text
            username_list = re.findall(r'alt=\\"(.*?)\\" src', text)
            follow_c = re.findall(r'关注 <em.*?follow\\" >(\d+)<\\/a><\\/em>', text)
            fans_c = re.findall(r'粉丝<em.*?\\" >(\d+)<\\/a><\\/em>', text)
            article_c = re.findall(r'微博<em.*? href=\\".*?\\" >(\d+)<\\/a>', text)
            href_list = re.findall(r'title=\\".*?\\" href=\\"(.*?\?refer_flag=.*?)\\" >', text)
            for i in range(len(follow_c)):
                if int(fans_c[i]) < 3000 and int(follow_c[i]) < 1000 and int(article_c[i]) > 1:
                    # 粉丝数量少于3000，关注少于1000，微博数大于1条
                    item = WeiboItem()
                    item["username"] = username_list[i]
                    item['href'] = 'https://weibo.com' + href_list[i].replace('\\/', '/')
                    item['md5_index'] = get_md5(item['href'])
                    item['done'] = False
                    # print(item)
                    yield item

            next_page_url = self._get_next_page(text)
            if next_page_url:
                yield scrapy.Request(url=next_page_url, callback=self.get_user)
