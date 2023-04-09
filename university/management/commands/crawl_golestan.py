import os
import time

from django.core.management.base import BaseCommand, CommandError
from crawler_scripts.golestan_crawler import GolestanCrawler


class Command(BaseCommand):
    help = 'Crawls golestan and extracts data into a Excel file.'
    USERNAME = 'username'
    PASSWORD = 'password'

    def add_arguments(self, parser):
        parser.add_argument(self.USERNAME, nargs='+', type=str, help='Username for golestan')
        parser.add_argument(self.PASSWORD, nargs='+', type=str, help='Password for golestan')

    def handle(self, *args, **options):
        pre = time.time()
        crawler = GolestanCrawler(user_login=True, username=options[self.USERNAME], password=options[self.PASSWORD])
        is_login = crawler.login()
        if is_login:
            crawler.get_courses()
        else:
            print('Could not extract data')
        print(time.time() - pre)
