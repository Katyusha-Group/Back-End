import os
import time

from django.core.management.base import BaseCommand, CommandError
from crawler_scripts.golestan_crawler import GolestanCrawler


class Command(BaseCommand):
    help = 'Crawls golestan and extracts data into a Excel file.'

    def handle(self, *args, **options):
        pre = time.time()
        crawler = GolestanCrawler(user_login=False)
        is_login = crawler.login()
        if is_login:
            crawler.get_courses()
        else:
            print('Could not extract data')
        print(time.time() - pre)
