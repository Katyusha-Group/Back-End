from crawler_scripts.lms_crawler_selenium import LMSCrawlerSelenium


def grab_teacher_photo(i, count):
    start = i * count
    crawler = LMSCrawlerSelenium()
    crawler.login('kamyar_moradian', 'K@my@r1381MORADIAN')
    crawler.get_teachers_photo(start=start, count=count)
