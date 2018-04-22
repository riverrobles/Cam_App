from pyicic.IC_ImagingControl import *
import os
import numpy as np
import time 

class Camera():
    def __init__(self,controller,name):
        self.name = name
        self.cam = controller.get_device(self.name)
        self.cam.open()
        
        #initialize frame data parameter 
        self.cam.start_live()
        data, width, height, depth = self.cam.get_image_data()
        self.frame_data = np.ndarray(buffer=data,dtype=np.uint8,shape=(height,width,depth))
        self.cam.stop_live()
        
        #initialize centroid parameters 
        self.cent_x = 0
        self.cent_y = 0
        self.cent_width = 0
        self.cent_height = 0
        
    def update_frame_data(self):
        self.cam.start_live()
        data, width, height, depth = self.cam.get_image_data()
        self.frame_data = np.ndarray(buffer=data,dtype=np.uint8,shape=(height,width,depth))
        self.cam.stop_live()

    def show_display(self):
        self.cam.start_live(show_display=True)

    def save_screen(self,file):
        self.cam.save_image(file)

    def update_centroid_params(self): 
        self.get_x()
        self.get_y()
        self.get_width()
        self.get_height()

    def get_x(self):
        colsums = []
        for i in range(640):
            sum = np.asarray([0,0,0])
            for j in range(480): 
                sum = np.add(sum,self.frame_data[j][i])
            colsums.append(np.median(sum))
        self.cent_x = np.argmax(colsums)

    def get_y(self):
        rowsums = []
        for row in self.frame_data: 
            rowsums.append(np.median(np.sum(row,axis=0)))
        self.cent_y = np.argmax(rowsums)
        
    def get_width(self):
        maxrow = self.frame_data[self.cent_y]
        i, uppermax = self.cent_x, 0 
        while uppermax==0:
            if maxrow[i][0]<maxrow[i+1][0]:
                uppermax = i
            else:
                i += 1
        i, lowermax = self.cent_x, 0
        while lowermax==0:
            if maxrow[i][0]<maxrow[i-1][0]:
                lowermax = i
            else:
                i -= 1
        self.cent_width = (uppermax-lowermax)/2
        
    def get_height(self):
        i, uppermax = self.cent_y, 0 
        while uppermax==0:
            if self.frame_data[i][self.centx][0]<self.frame_data[i+1][self.centx][0]:
                uppermax = i
            else:
                i += 1 
        i, lowermax = self.cent_y, 0
        while lowermax==0:
            if self.frame_data[i][self.centx][0]<self.frame_data[i-1][self.centx][0]:
                lowermax = i
            else:
                i -= 1
        self.cent_height = (uppermax-lowermax)/2

    def close_cam(self):
        self.cam.stop_live()
        self.cam.close()
