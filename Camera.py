from pyicic.IC_ImagingControl import *
import os
import time 

class Camera():
    def __init__(self,controller,name):
        self.cam = controller.get_device(name)
        self.cam.open()
        self.cam.set_video_format(self.cam.list_video_formats()[0])
        self.cam.enable_continuous_mode(True)

    def show_display(self):
        self.cam.start_live(show_display=True)

    def save_screen(self,file):
        self.cam.save_image(file)
