import numpy as np
import PIL.Image
import time
from pyicic.IC_ImagingControl import *

ic = IC_ImagingControl()
ic.init_library()
names = ic.get_unique_device_names()

cam = ic.get_device(names[0])
cam.open()
cam.enable_continuous_mode(True)

cam.start_live()
time.sleep(0.04)
cam.save_image(b'output7.jpg')
cam.stop_live()
cam.close()
ic.close_library()

