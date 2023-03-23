import os
import random

import requests


class ImageHandler:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.create_path()

    def download(self, captcha_url):
        try:
            print('creating image with url :::', captcha_url)
            image = requests.get(captcha_url).content
            return self.save(png=image)
        except Exception as e:
            print("Error downloading image: ", e)

    def save(self, png):
        try:
            img_name = str(int(random.uniform(10000, 99999))) + ".gif"
            img_path = os.path.join(self.output_dir, img_name)
            print('creating image with path :::', img_path)
            with open(img_path, 'wb') as fh:
                fh.write(png)
            return img_path
        except Exception as e:
            print("Error downloading image: ", e)

    @staticmethod
    def delete(img_path):
        try:
            print('deleting image with path :::', img_path)
            os.remove(img_path)
        except Exception as e:
            print("Error deleting image: ", e)

    def create_path(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
