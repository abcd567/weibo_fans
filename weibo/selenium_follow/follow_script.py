# _*_ coding: utf-8 _*_
__author__ = "吴飞鸿"
__date__ = "2019/12/4 18:39"

# _*_ coding: utf-8 _*_
import time
import datetime
import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from weibo.secure import weibo_account, weibo_password
from weibo.settings import MYSQL_DBNAME, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD


def login_weibo(browser):
    browser.get('https://weibo.com')
    if WebDriverWait(browser, 20).until(lambda x: x.find_element_by_xpath('//a[@node-type="loginBtn"]')):
        browser.implicitly_wait(10)
        browser.find_element_by_id('loginname').clear()
        time.sleep(1)
        browser.find_element_by_xpath('//input[@id="loginname"]').send_keys(weibo_account)
        time.sleep(1)
        browser.find_element_by_xpath('//input[@type="password"]').send_keys(weibo_password)
        time.sleep(1)
        # 如果验证码，在下一行加入处理逻辑
        browser.find_element_by_css_selector('a.W_btn_a.btn_32px').click()
        time.sleep(10)
    pass


def get_data_from_mysql(cursor):
    search_sql = "select * from user_info WHERE followed=0 limit 10"
    cursor.execute(search_sql)
    result = cursor.fetchall()
    return result


def sign(cursor, oid, followed=1):
    update_sql = 'update user_info set followed=%s WHERE oid=%s'
    cursor.execute(update_sql, (followed, oid))
    conn.commit()


def analyse_data(cursor, data):
    bir_day_limit = datetime.date(1990, 1, 1)
    onick = data[1]
    location = data[8]
    birthday = data[12]
    highschool = data[22]
    oid = data[2]
    url = ''
    if '广东' in location or '海外' in location or '其他'in location or location == '':
        if not birthday:
            birthday = datetime.date.today()
        if bir_day_limit <= birthday or '吴川' in highschool:
            url = 'https://weibo.com/u/{}'.format(str(oid))
    # 标记数据库中已处理数据
    sign(cursor, oid)
    return url, onick, oid


def follow_user(user_url, user_name, oid):
    browser.get(user_url)
    try:
        if WebDriverWait(browser, 20).until(
                lambda x: x.find_element_by_xpath('//div[contains(@class, "shadow ")]//a[@action-type="follow"]')):
            browser.find_element_by_xpath('//div[contains(@class, "shadow ")]//a[@action-type="follow"]').click()
            sign(cursor, oid)
            print("关注>>>>>>>", user_name)
    except Exception as e:
        sign(cursor, oid, followed=0)
        print(e, '<<<<<<<<<', user_name)


def create_browser():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path='I:\\谷歌下载\\chromedriver_win32\\chromedriver.exe',
                               chrome_options=chrome_options)
    try:
        browser.maximize_window()
    except:
        pass
    return browser


def create_db_cursor():
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DBNAME,
        charset="utf8mb4",
        use_unicode=True
    )
    cursor = conn.cursor()
    return conn, cursor


if __name__ == '__main__':
    browser = create_browser()
    conn, cursor = create_db_cursor()

    login_weibo(browser)
    res = get_data_from_mysql(cursor)
    while res:
        for r in res:
            url, name, oid = analyse_data(cursor, r)
            if url:
                follow_user(url, name,oid)
        res = get_data_from_mysql(cursor)

    print("ok")
    # 退出
    browser.close()
    cursor.close()
    conn.close()

    pass