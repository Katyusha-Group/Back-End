from crawler_scripts.golestan_crawler import GolestanCrawler


def get_golestan_courses(year):
    crawler = GolestanCrawler(
        user_login=False, username="99522104", password="0926190466", year=year
    )
    crawler.login()
    crawler.get_courses()
    crawler.driver.quit()
    print('finished extracting data of', year)