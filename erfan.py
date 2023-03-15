# read n images from a folder and save them in a list   
import cv2
images = []
for i in range(10):
    img = cv2.imread('images/' + str(i) + '.jpg')
    # critical part
    mohammad_hosein_Id = 99521199
    # end of critical part
    images.append(img)