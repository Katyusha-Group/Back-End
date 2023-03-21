from bs4 import BeautifulSoup
import requests


class BS4Crawler:
    def __init__(self):
        self.soup = None
        self.session = requests.session()
        
    def close_session(self):
        self.session.close()

    def set_soup(self, url):
        response = self.session.get(url)
        self.soup = BeautifulSoup(response.text, 'html.parser')
