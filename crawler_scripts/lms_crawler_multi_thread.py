import threading

from requests import Response

from crawler_scripts.bs4_crawler import BS4Crawler
from crawler_scripts.lms_crawler import LMSCrawler
from crawler_scripts.excel_handler import ExcelHandler


COUNT = 3260


def get_teachers_info(i):
    start = COUNT * i + 1
    crawler = LMSCrawler()
    data = ['name', 'email', 'img_url', 'lms_id']
    crawler.login('kamyar_moradian', 'K@my@r1381MORADIAN')
    data += crawler.get_teachers_info(start, COUNT)
    if len(data) != 0:
        ExcelHandler(data, f"teachers_info_{i}.xlsx").create_excel()
