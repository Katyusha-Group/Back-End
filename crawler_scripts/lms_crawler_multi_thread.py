from crawler_scripts.lms_crawler import LMSCrawler
from crawler_scripts.lms_crawler_selenium import LMSCrawlerSelenium
from utils.Excel.excel_handler import ExcelHandler

COUNT = 3260


def get_teachers_info(i):
    start = COUNT * i + 1
    crawler = LMSCrawler()
    data = ['name', 'email', 'img_url', 'lms_id']
    crawler.login('kamyar_moradian', 'K@my@r1381MORADIAN')
    data += crawler.get_teachers_info(start, COUNT)
    if len(data) != 0:
        ExcelHandler(data, f"teachers_info_{i}.xlsx").create_excel()


def grab_teacher_photo(i, count):
    start = i * count
    crawler = LMSCrawlerSelenium()
    crawler.login('kamyar_moradian', 'K@my@r1381MORADIAN')
    crawler.get_teachers_photo(start=start, count=count)
