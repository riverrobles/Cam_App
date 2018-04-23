from pyicic.IC_ImagingControl import *
import logging
import tkinter as ttk
import time
from Camera import Camera
import PIL.Image
import PIL.ImageTk

class CopyPasteBox(ttk.Entry):
    def __init__(self, master, **kw):
        ttk.Entry.__init__(self, master, **kw)
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-v>', self.paste)

    def copy(self, event=None):
        self.clipboard_clear()
        text = self.get("sel.first", "sel.last")
        self.clipboard_append(text)

    def cut(self, event):
        self.copy()
        self.delete("sel.first", "sel.last")

    def paste(self, event):
        text = self.selection_get(selection='CLIPBOARD')
        #self.insert('insert', text)

class App():
    def __init__(self,master):
        self.root = master
        self.controller = IC_ImagingControl()
        self.controller.init_library()
        names = self.controller.get_unique_device_names()
        
        self.cam = Camera(self.controller,names[0])
        #self.ncams = len(names)
        
        #self.cams = [Camera(self.controller,names[i]) for i in range(self.ncams)]

        # Frames

        self.video_frame = ttk.Frame(master,width=480,height=640)
        self.video_frame.grid(row=0,column=0,rowspan=3,padx=5)

        self.setup_frame = ttk.Frame(master)
        self.setup_frame.grid(row=0,column=1,pady=5)

        self.save_frame = ttk.Frame(master)
        self.save_frame.grid(row=1,column=1,pady=5)

        self.calc_frame = ttk.Frame(master)
        self.calc_frame.grid(row=2,column=1,pady=5)

        #Active Parameters

        self.save_file = ttk.StringVar()
        self.save_file.set('test')

        self.save_directory = ttk.StringVar()
        self.save_directory.set('testdir')

        self.gain = ttk.StringVar()
        self.gain.set('200.0')

        self.act_gain = ttk.StringVar()
        self.act_gain.set('200.0')

        self.cap_interval = ttk.StringVar()
        self.cap_interval.set('10.0')

        self.num_saves = ttk.StringVar()
        self.num_saves.set('20')

        self.start_point = ttk.StringVar()
        self.start_point.set('0.0')

        self.centroid_x = ttk.StringVar()
        self.centroid_x.set('n/a')

        self.centroid_y = ttk.StringVar()
        self.centroid_y.set('n/a')

        self.centroid_width = ttk.StringVar()
        self.centroid_width.set('n/a')

        self.centroid_height = ttk.StringVar()
        self.centroid_height.set('n/a')

        #Camera Setup Frame Widgets

        gain_label = ttk.Label(self.setup_frame,text="Gain SetPoint: ")
        gain_label.grid(row=0,column=0,sticky=ttk.E)

        gain_entry = CopyPasteBox(self.setup_frame,textvariable=self.gain)
        gain_entry.bind("<Return>",self.set_gain)
        gain_entry.grid(row=0,column=1)

        actgain_label = ttk.Label(self.setup_frame,text="Current Gain: ")
        actgain_label.grid(row=1,column=0,sticky=ttk.E)

        self.actgain_label2 = ttk.Label(self.setup_frame,text="{}".format(self.act_gain.get()))
        self.actgain_label2.grid(row=1,column=1,sticky=ttk.W)

        background_button = ttk.Button(self.setup_frame,text="Save Screen for Background Subtraction",command=self.save_background)
        background_button.grid(row=2,columnspan=2)

        #Save Frame Widgets

        dir_label = ttk.Label(self.save_frame,text="Save Directory: ")
        dir_label.grid(row=0,column=0,sticky=ttk.E)

        dir_entry = CopyPasteBox(self.save_frame,textvariable=self.save_directory)
        dir_entry.bind("<Return>",self.update_preview)
        dir_entry.grid(row=0,column=1)

        file_label = ttk.Label(self.save_frame,text="Base Save File: ")
        file_label.grid(row=1,column=0,sticky=ttk.E)

        file_entry = CopyPasteBox(self.save_frame,textvariable=self.save_file)
        file_entry.bind("<Return>",self.update_preview)
        file_entry.grid(row=1,column=1)

        preview_label = ttk.Label(self.save_frame,text="Save File Name Preview: ")
        preview_label.grid(row=2,column=0,sticky=ttk.E)

        self.preview_name = ttk.Label(self.save_frame,text="{}/{}.bmp".format(self.save_directory.get(),self.save_file.get()))
        self.preview_name.grid(row=2,column=1,sticky=ttk.W)

        interval_label = ttk.Label(self.save_frame,text='Capture Interval (s): ')
        interval_label.grid(row=3,column=0,sticky=ttk.E)

        interval_entry = CopyPasteBox(self.save_frame,textvariable=self.cap_interval)
        interval_entry.grid(row=3,column=1)

        savenum_label = ttk.Label(self.save_frame,text='Number of Saves: ')
        savenum_label.grid(row=4,column=0,sticky=ttk.E)

        savenum_entry = CopyPasteBox(self.save_frame,textvariable=self.num_saves)
        savenum_entry.grid(row=4,column=1)

        start_label = ttk.Label(self.save_frame,text='Camera Starting Point: ')
        start_label.grid(row=5,column=0,sticky=ttk.E)

        start_entry = CopyPasteBox(self.save_frame,textvariable=self.start_point)
        start_entry.grid(row=5,column=1)

        scan_button = ttk.Button(self.save_frame,text='Perform Scan',command=self.scan_length)
        scan_button.grid(row=6,columnspan=2)

        #Calculation Frame Widgets

        xlabel = ttk.Label(self.calc_frame,text='Centroid x: ')
        xlabel.grid(row=0,column=0,sticky=ttk.E)

        self.xlabel2 = ttk.Label(self.calc_frame,text='{}'.format(self.centroid_x.get()))
        self.xlabel2.grid(row=0,column=1,sticky=ttk.W)

        ylabel = ttk.Label(self.calc_frame,text='Centroid y: ')
        ylabel.grid(row=1,column=0,sticky=ttk.E)

        self.ylabel2 = ttk.Label(self.calc_frame,text='{}'.format(self.centroid_y.get()))
        self.ylabel2.grid(row=1,column=1,sticky=ttk.W)

        wlabel = ttk.Label(self.calc_frame,text='Centroid width: ')
        wlabel.grid(row=2,column=0,sticky=ttk.E)

        self.wlabel2 = ttk.Label(self.calc_frame,text='{}'.format(self.centroid_width.get()))
        self.wlabel2.grid(row=2,column=1,sticky=ttk.W)

        hlabel = ttk.Label(self.calc_frame,text='Centroid height: ')
        hlabel.grid(row=3,column=0,sticky=ttk.E)

        self.hlabel2 = ttk.Label(self.calc_frame,text='{}'.format(self.centroid_height.get()))
        self.hlabel2.grid(row=3,column=1,sticky=ttk.W)

        #Video Frame

        self.canvas = ttk.Canvas(self.video_frame,width=640,height=480,bg='white')
        self.canvas.pack()
        self.cam.save_image()
        img = PIL.Image.open('canvas.jpg')
        self.canvas.image = PIL.ImageTk.PhotoImage(img)
        self.canvas.create_image(0,0,image=self.canvas.image,anchor='nw')
        
        self.update_parameters()

    def update_preview(self,event):
        directory = self.save_directory.get()
        basename = self.save_file.get()
        self.preview_name['text']=["{}/{}.bmp".format(directory,basename)]
        
    def update_parameters(self): 
        self.cam.update_frame_data()
        #self.cam.update_centroid_params()
        #self.centroid_x.set(self.cam.cent_x)
        #self.centroid_y.set(self.cam.cent_y)
        #self.centroid_width.set(self.cam.cent_width)
        #self.centroid.height.set(self.cam.cent_height)
        self.canvas.delete('all')
        self.cam.save_image()
        img = PIL.Image.open('canvas.jpg')
        self.canvas.image = PIL.ImageTk.PhotoImage(img)
        self.canvas.create_image(0,0,image=self.canvas.image,anchor='nw')
        self.root.after(10,self.update_parameters)

    def set_gain(self,event):
        return None

    def save_background(self):
        self.cam.update_background_frame()

    def scan_length(self):
        return None
        
    def close_cameras(self):
        for cam in self.cams:
            cam.close_cam()

def main():
    logging.basicConfig(level=logging.DEBUG)
    root = ttk.Tk()
    app = App(root)
    root.mainloop()
    app.cam.cam.stop_live()
    app.cam.cam.close()
    #app.close_cameras()
    app.controller.close_library()

if __name__=='__main__':
    main()
