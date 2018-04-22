import time

import numpy as np

from pyicic.IC_ImagingControl import *
from pyicic.IC_Camera import C_FRAME_READY_CALLBACK

ic = IC_ImagingControl()
ic.init_library()

cam_names = ic.get_unique_device_names()
print(cam_names)
device_name = cam_names[0]

print(device_name)

cam = ic.get_device(device_name)
cam.open()
cam.reset_properties()

formats = cam.list_video_formats()
print(formats)
cam.set_video_format(formats[0])

print('get_available_frame_filter_count:', cam.get_available_frame_filter_count())
print('get_available_frame_filters:', cam.get_available_frame_filters(cam.get_available_frame_filter_count()))

h = cam.create_frame_filter(b'Rotate Flip')
h2 = cam.create_frame_filter(b'ROI')
cam.add_frame_filter_to_device(h)
cam.add_frame_filter_to_device(h2)
cam.frame_filter_set_parameter(h2, b'Top', 400)
cam.frame_filter_set_parameter(h2, b'Left', 120)
cam.frame_filter_set_parameter(h2, b'Height', 1000)
cam.frame_filter_set_parameter(h2, b'Width', 1000)

#print(cam.frame_filter_get_parameter(h, 'Rotation Angle'))
cam.frame_filter_set_parameter(h, b'Rotation Angle', 90)
#print(cam.frame_filter_get_parameter(h, 'Rotation Angle'))

cam.start_live(show_display=True)

def handle_frame(handle_ptr, p_data, frame_num, data):
    print('callback called!', frame_num)
    print(time.time())
    
cam.register_frame_ready_callback(C_FRAME_READY_CALLBACK(handle_frame))

cam.snap_image(1000)
cam.snap_image(1000)
cam.snap_image(1000)

input('Waiting for callback')

cam.save_image(b'output.jpg')
        
data, width, height, depth = cam.get_image_data()

print(width, height)

frame = np.ndarray(buffer=data,
                   dtype=np.uint8,
                   shape=(height, width, depth))
                   
cam.stop_live()

cam.close()

ic.close_library()
