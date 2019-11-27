# -*- coding: utf-8 -*-
import pickle

import os

import re
from html import unescape

from lxml import etree
from urllib.parse import urljoin

import scrapy
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from weibo.items import WeiboItem
from weibo.secure import weibo_account, weibo_password
from weibo.settings import project_dir
from weibo.utils.handle_mongo import HandleMongo
from weibo.utils.js_2_xml_and_unescape import js2xml_unescape
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
            注：测试发现weibo cookies有效期只有24小时，24小时后可以删除 weibo.cookie 文件，重新模拟登陆
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
            results = client.find({'done': False}, limit=10)
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
    def _get_follow_page(data_script):
        # url_list = re.findall(r'<a bpfilter=\\"page_frame\\".*?href=\\"(.*?)\\" >.*?<span.*?关注<\\/span>', text)
        # 曾经运行上行注释代码会出现偶尔会出现在这里卡死的情况
        # 正则: r'<a bpfilter=\\"page_frame\\".*?href=\\"(.*?)\\" >.*?<span.*?关注<\\/span>'
        # 原因猜测：正则缓存问题 or 匹配算法复杂度指数上升
        # 卡死处执行了 re.py > _compile()代码： 290~291行
        # p, loc = _cache[type(pattern), pattern, flags]
        # if loc is None or loc == _locale.setlocale(_locale.LC_CTYPE):
        #     return p

        # # 这么写没有发现问题
        # url_list = re.findall(r'href=\\"(.*?)\\" ><strong.*?关注', text)

        # 改用js2xml
        follow_page = []
        for d in data_script:
            if 'FM.view({"ns":"","domid":"Pl_Core_T8CustomTriColumn__3"' in d:
                selector = js2xml_unescape(d)
                follow_page = selector.xpath('//table[@class="tb_counter"]//td[1]/a/@href')
        try:
            return follow_page[0].replace('//', 'https://')
        except Exception as e:
            print(e)

    def handle_user_home(self, response):
        if response.status == 200:
            data_script = response.xpath('//script/text()').extract()
            follow_page = self._get_follow_page(data_script)
            # 这里先不提取个人信息，待数据量足够多，再写另一个爬虫提取信息
            yield scrapy.Request(url=follow_page, callback=self.get_user)

    def _get_next_page(self, selector):
        # 由于被系统限制，每个账号只能查看5页粉丝
        if self.count <= 5:
            self.count += 1
            href = selector.xpath('//a[@class="page next S_txt1 S_line1"]/@href')
            if href:
                href = href[0]
                next_url = urljoin('https://weibo.com', href)
                return next_url
            # 没有下一页返回0

        # 5轮重置count
        if self.count > 5:
            self.count = 1

        # 只要没有下一页就返回false,不管满不满5页
        return False

    def get_user(self, response):
        if response.status == 200:
            data_script = response.xpath('//script/text()').extract()[-1]
            selector = js2xml_unescape(data_script)
            nodes = selector.xpath('//li[@class="follow_item S_line2"]')

            for n in nodes:
                content = etree.tostring(n, pretty_print=True, encoding='utf8')
                s = etree.HTML(unescape(content.decode()))
                username = s.xpath('//li[@class="follow_item S_line2"]//dt/a/@title')[0]
                href = s.xpath('//li[@class="follow_item S_line2"]//dt/a/@href')[0]
                follow_c = s.xpath('//span[1]/em[@class="count"]/a/text()')
                fans_c = s.xpath('//span[2]/em[@class="count"]/a/text()')
                article_c = s.xpath('//span[3]/em[@class="count"]/a/text()')

                if follow_c and fans_c and article_c:
                    # 有些公众账号涉及隐私，没有关注粉丝等数据,且不是收集目标,直接排除。
                    # 如 同性恋婚姻合法化:https://weibo.com/p/1008089993f2f8dc0d7a92bc4a28748d6e8fd0/super_index
                    if int(fans_c[0]) < 3000 and int(follow_c[0]) < 1000 and int(article_c[0]) > 1:
                        # 粉丝数量少于3000，关注少于1000，微博数大于1条
                        item = WeiboItem()
                        item["username"] = username
                        item['href'] = urljoin('https://weibo.com', href)
                        item['md5_index'] = get_md5(item['href'])
                        item['done'] = False
                        yield item

            next_page_url = self._get_next_page(selector)
            if next_page_url:
                yield scrapy.Request(url=next_page_url, callback=self.get_user)
