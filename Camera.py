from pyicic.IC_ImagingControl import *
import os
import numpy as np
import time 

class Camera():
    def __init__(self,controller,name):
        self.name = name
        self.cam = controller.get_device(self.name)
        self.cam.open()

    def show_display(self):
        self.cam.start_live(show_display=True)

    def save_screen(self,file):
        self.cam.save_image(file)

    def get_centroid_pos(self): 
        data, width, height, depth = self.cam.get_image_data()
        frame = np.ndarray(buffer=data,dtype=np.uint8,shape=(height,width,depth))
        return self.get_x(frame), self.get_y(frame)

    def get_x(self,framedata):
        colsums = []
        for i in range(640):
            sum = np.asarray([0,0,0])
            for j in range(480): 
                sum = np.add(sum,framedata[j][i])
            colsums.append(np.median(sum))
        return np.argmax(colsums)

    def get_y(self,framedata):
        rowsums = []
        for row in framedata: 
            rowsums.append(np.median(np.sum(row,axis=0)))
        return np.argmax(rowsums)

    def close_cam(self):
        self.cam.stop_live()
        self.cam.close()
