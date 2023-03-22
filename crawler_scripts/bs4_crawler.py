from bs4 import BeautifulSoup
import mechanicalsoup
import requests


class BS4Crawler:
    def __init__(self):
        self.soup = None
        self.session = requests.session()
        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
        )
        
    def close_session(self):
        self.session.close()

    def set_soup(self, url):
        response = self.session.get(url)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def transfer_session(self):
        self.session = self.browser.session

    def close_browser(self):
        self.browser.close()
