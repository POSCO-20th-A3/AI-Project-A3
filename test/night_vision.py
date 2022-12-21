import cv2
import numpy as np
import sys

def saturate_contrast(p, num):
    pic = p.copy()
    pic = pic.astype('int64')
    pic = np.clip(pic*num, 0, 255)
    pic = pic.astype('uint8')
    return pic

def up(img):
    dst = saturate_contrast(img,3)
    dst = cv2.add(dst, (50, 50, 50,0))

    return dst