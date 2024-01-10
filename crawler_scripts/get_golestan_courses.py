from crawler_scripts.golestan_crawler import GolestanCrawler


def get_golestan_courses(year):
    crawler = GolestanCrawler(
        user_login=False, year=year
    )
    crawler.login()
    print('Successfully logged in for year', year)
    crawler.get_courses()
    crawler.driver.quit()
    print('finished extracting data of', year)
