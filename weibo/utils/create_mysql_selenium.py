# _*_ coding: utf-8 _*_
import pymysql
from appium import webdriver
from selenium.webdriver.chrome.options import Options

from weibo.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME

__author__ = "吴飞鸿"
__date__ = "2019/12/4 19:01"

#
# class PreCreate():
#     def __init__(self):
#         self.browser = self.create_db_cursor()
#         self.conn, self.cursor = self.create_db_cursor()
#
#     @staticmethod
#     def create_browser():
#         chrome_options = Options()
#         chrome_options.add_argument('--no-sandbox')
#         chrome_options.add_argument('--headless')
#         browser = webdriver.Chrome(executable_path='I:\\谷歌下载\\chromedriver_win32\\chromedriver.exe',
#                                    chrome_options=chrome_options)
#         try:
#             browser.maximize_window()
#         except:
#             pass
#         return browser
#
#     @staticmethod
#     def create_db_cursor():
#         conn = pymysql.connect(
#             host=MYSQL_HOST,
#             user=MYSQL_USER,
#             password=MYSQL_PASSWORD,
#             database=MYSQL_DBNAME,
#             charset="utf8mb4",
#             use_unicode=True
#         )
#         cursor = conn.cursor()
#         return conn, cursor
#
#     def __del__(self):
#         self.browser.close()
#         self.cursor.close()
#         self.conn.close()