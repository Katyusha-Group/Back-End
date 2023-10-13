import os
import random
from os.path import basename

import requests


class ImageHandler:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.create_path()

    def download_captcha(self, url):
        try:
            print('creating image with url :::', url)
            image = requests.get(url).content
            name = str(int(random.uniform(10000, 99999)))
            return self.save(img=image, suffix='.gif', name=name)
        except Exception as e:
            print("Error downloading image: ", e)
            return False

    def download_img(self, url, name):
        try:
            print('creating image with url :::', url)
            image = requests.get(url).content
            return self.save(img=image, name=name, suffix='.png')
        except Exception as e:
            print("Error downloading image: ", e)
            return False

    def save(self, img, name, suffix):
        try:
            img_name = name + suffix
            img_path = os.path.join(self.output_dir, img_name)
            print('creating image with path :::', img_path)
            with open(img_path, 'wb') as fh:
                fh.write(img)
            return img_path
        except Exception as e:
            print("Error creating image: ", e)
            return False

    @staticmethod
    def delete(img_path):
        try:
            print('deleting image with path :::', img_path)
            os.remove(img_path)
        except Exception as e:
            print("Error deleting image: ", e)
            return False

    def create_path(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
