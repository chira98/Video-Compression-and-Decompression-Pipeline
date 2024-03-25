from skimage import color, io
import numpy as np
import cv2

class YCbCr:
    def __init__(self,image):
        self.image=image

    def convert(self):
        ycbcr = cv2.cvtColor(self.image, cv2.COLOR_BGR2YCrCb)
        Y = ycbcr[:, :, 0]
        Cb = ycbcr[:, :, 1]
        Cr = ycbcr[:, :, 2]
        #cv2.imwrite("Y.jpg", Y)
        #cv2.imwrite("Cb.jpg", Cb)
        #cv2.imwrite("Cr.jpg", Cr)
        return Y,Cb,Cr
