# read n images from a folder and save them in a list   
import cv2
images = []
for i in range(10):
    img = cv2.imread('images/' + str(i) + '.jpg')
    # critical part
    
    # end of critical part
    images.append(img)