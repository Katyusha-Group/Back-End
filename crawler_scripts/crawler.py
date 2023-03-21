from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class Crawler:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=self.options)
