# -*- coding: utf-8 -*-
import scrapy


class GetInfoSpider(scrapy.Spider):
    name = 'get_info'
    allowed_domains = ['weibo.com']
    start_urls = ['http://weibo.com/']

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
            'weibo.pipelines.MysqlTwistedPipeline': 300,
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
        pass
