from pyicic.IC_ImagingControl import *
import os
import numpy as np
import logging
import time
import PIL.Image
import cv2

class Camera():
    def __init__(self,controller,name):
        self.name = name
        self.cam = controller.get_device(self.name)
        self.cam.open()
        self.cam.gain.auto = False
        self.cam.enable_continuous_mode(True)
        
        #initialize frame data parameter 
        self.cam.start_live()
        time.sleep(0.1)
        data, width, height, depth = self.cam.get_image_data()
        self.frame_data = np.ndarray(buffer=data,dtype=np.uint8,shape=(height,width,depth))
        
        #initialize background frame data
        self.background_frame = self.frame_data
        
        #initialize centroid parameters
        self.fitx, self.fity = [], []
        self.xcent, self.ycent = 0, 0
        self.spot = []
        self.extremaindex = 0
        self.major = 0
        self.minor = 0
        self.angle = 0
        
    def update_frame_data(self):
        data, width, height, depth = self.cam.get_image_data()
        raw_frame_data = np.ndarray(buffer=data,dtype=np.uint8,shape=(height,width,depth))
        self.frame_data = raw_frame_data
        #self.frame_data = (np.add(raw_frame_data,self.background_frame * -1)).astype(np.uint8)
        
    def update_background_frame(self):
        data, width, height, depth = self.cam.get_image_data()
        self.background_frame = np.ndarray(buffer=data,dtype=np.uint8,shape=(height,width,depth))

    def update_centroid_params(self): 
        try:
            self.get_x()
            self.get_y()
            self.get_width()
            self.get_height()
        except IndexError as e:
            logging.debug(e)

    def save_file(self,filename):
        self.update_frame_data()
        np.save("{}data".format(filename),self.frame_data)
        np.save("{}spotdata".format(filename),self.spot)
        savestr = "{}.jpg".format(filename)
        self.cam.save_image(savestr.encode('utf-8'),1)

    def update(self):
        self.update_frame_data()
        self.find_spot()
        self.least_squares()

    def find_spot(self):
        data = self.frame_data
        img = cv2.cvtColor(data,cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(img,127,255,0)
        _, contours, hierarchy = cv2.findContours(thresh,2,1)
        big_contour = []
        max = 0
        for i in contours:
            area = cv2.contourArea(i)
            if area > max:
                max = area
                big_contour = i
        self.spot = big_contour

    def least_squares(self):
        if self.spot!=[]:
            try: 
                x = np.asarray([point[0][0] for point in self.spot],dtype = 'float64')
                y = np.asarray([point[0][1] for point in self.spot],dtype = 'float64')
                xmean, ymean = np.mean(x), np.mean(y)
                x -= xmean
                y -= ymean
                U, S, V = np.linalg.svd(np.stack((x,y)))

                tt = np.linspace(0,2*np.pi,1000)
                circle = np.stack((np.cos(tt),np.sin(tt)))
                transform = np.sqrt(2/len(self.spot))*U.dot(np.diag(S))
                fit = transform.dot(circle)+np.array([[xmean],[ymean]])
                
                self.fitx, self.fity = fit[0], fit[1]
                self.xcent, self.ycent = np.mean(self.fitx), np.mean(self.fity)
                maxdist, index = 0, 0
                for i in range(int(len(self.fitx)/4)):
                    if np.sqrt((self.xcent-self.fitx[i])**2+(self.ycent-self.fity[i])**2) > maxdist:
                        maxdist = np.sqrt((self.xcent-self.fitx[i])**2+(self.ycent-self.fity[i])**2)
                        index = i
                extrema = [np.sqrt((self.fitx[i]-self.xcent)**2+(self.fity[i]-self.ycent)**2),np.sqrt((self.fitx[i+250]-self.xcent)**2+(self.fity[i+250]-self.ycent)**2)]
                self.extremaindex = index
                self.major, self.minor = np.max(extrema), np.min(extrema)
                self.angle = np.arctan2(-(self.fity[0]-self.ycent),(self.fitx[0]-self.xcent))
            except ValueError as e:
                logging.debug(e)
                logging.debug("No spot present, value error occured")
        else:
            logging.debug("No spot present")

    def close_cam(self):
        self.cam.stop_live()
        self.cam.close()
