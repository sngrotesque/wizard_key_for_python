# https://theailearner.com/2018/10/15/creating-video-from-images-using-opencv-python/

import cv2
from typing import List

def jpg2mp4(in_path :List[str], out_path :str, fps :int = 24):
    img_array = []
    for filename in in_path:
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)
    out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

from os import walk
path = walk('2022_07_25_15_46_16_99985668_ugoira1920x1080').__next__()
path = [f'{path[0]}/{x}' for x in path[2]]

jpg2mp4(path, 'test.mp4')
