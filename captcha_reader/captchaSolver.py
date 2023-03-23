import os
import pickle

import numpy as np
from skimage.transform import resize

from captcha_reader.cropLettersFromImage import getWords


class CaptchaSolver:
    BASE_DIR = "C:/Users/Kamyar/Dropbox/PC/Documents/Uni/Sem6/Analysis and Designing System/Katyusha/Back-End/captcha_reader/"
    DATA_DIRECTORY = "./DataSet/"
    MODEL_PATH = "./finalized_model.sav"
    
    def __init__(self):
        os.chdir(self.BASE_DIR)
        self.categories = os.listdir(self.DATA_DIRECTORY)
        try:
            self.loaded_model = pickle.load(open(self.MODEL_PATH, "rb"))
        except:
            print("You should train model and save the model first!")
            exit(0)

    def get_captcha_text(self, captcha):
        clusters = getWords(captcha)
        text = ""
        for image in clusters:
            flat_data = []
            img_resized = resize(image, (40, 40, 3))
            flat_data.append(img_resized.flatten())
            flat_data = np.array(flat_data)
            y_output = self.loaded_model.predict(flat_data)
            text += self.categories[y_output[0]].replace("upper", "").replace("lower", "")
        return text
