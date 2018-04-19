from pyicic.IC_ImagingControl import *

class Camera():
	def __init__(self,controller,name):
		self.cam = controller.get_device(name)
		self.cam.open()
		self.descriptors = self.cam.list_property_names()
		self.cam.exposure.value = (self.cam.exposure.min+self.cam.exposure.max)/2
		self.cam.set_video_format(self.cam.list_video_formats()[0])
		self.cam.enable_continuous_mode(True)
		self.cam.start_live(show_display=True)