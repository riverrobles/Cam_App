import PIL.Image
import matplotlib.pyplot as plt 
import numpy as np
import os 

class Directory():
	'''
	
	class to gather data on spot size and relative spot brightness from a directory containing image files. 
	
	inputs:
		path: full path to the directory in question (ex. "C:/Users/user/Desktop/2018-04-12-spot-data/Test1")
		nsteps: number of image files in the directory
		x0: initial camera position along the bar

	'''
	def __init__(self,path,nsteps,x0):
		self.path = path 
		self.nsteps = nsteps
		self.x0 = x0
		self.xdata = [(self.x0+x)*25.5/40 for x in range(self.nsteps)]
		self.row_data = [self.get_data(file)[0] for file in os.listdir(self.path)]
		self.col_data = [self.get_data(file)[1] for file in os.listdir(self.path)]
		self.centrows, self.centcols = self.get_centers() #lists of central rows, central columns for each file
		self.amps = self.get_amplitudes() #list of amplitudes 
		self.radii = self.radii() #list of radii
		self.avg_radius, self.avg_amp, self.std_radius, self.std_amp = self.statistics()
		self.filtered_amps, self.filtered_radii = self.filter_data()
		self.filt_avg_radius, self.filt_avg_amp, self.filt_std_radius, self.filt_std_amp = self.filtered_statistics()

	def full_file_path(self,file):
		return self.path+"/"+file

	def get_data(self,file):
		image = PIL.Image.open(self.full_file_path(file))
		rows = [[image.getpixel((i,j)) for i in range(640)] for j in range(480)]
		columns = [[image.getpixel((i,j)) for j in range(480)] for i in range(640)]
		return rows,columns

	def sums(self):
		return [[np.mean(row)*640 for row in file] for file in self.row_data], [[np.mean(col)*480 for col in file] for file in self.col_data]

	def get_centers(self):
		row_sums, col_sums = self.sums()
		rindices, cindices = [np.argmax(row) for row in row_sums], [np.argmax(col) for col in col_sums]
		assert len(rindices) == len(cindices)
		return [self.row_data[i][rindices[i]] for i in range(len(rindices))], [self.col_data[i][cindices[i]] for i in range(len(rindices))]

	def get_amplitudes(self): 
		ramps, camps = [np.max(row) for row in self.centrows], [np.max(col) for col in self.centcols]
		return [(ramps[i]+camps[i])/2 for i in range(len(ramps))]

	'''
	these next two functions can be modified easily to give us the horizontal/vertical dimensions individually in the case that the beam isn't cylindrically symmetric
	'''

	def lower_radii(self):
		lrradii = []
		for row in self.centrows:
			tracker = 0
			i = np.argmax(row)
			while tracker == 0:
				if row[i-1]>row[i]:
					tracker = 1
				else:
					i -= 1
			lrradii.append(np.max(row)-row[i])
		lcradii = []
		for col in self.centcols:
			tracker = 0
			i = np.argmax(col)
			while tracker ==0:
				if col[i-1]>col[i]:
					tracker = 1
				else:
					i -= 1
			lcradii.append(np.max(col)-col[i])
		return lrradii, lcradii

	def upper_radii(self):
		urradii = []
		for row in self.centrows:
			tracker = 0
			i = np.argmax(row)
			while tracker == 0:
				if row[i+1]>row[i]:
					tracker = 1
				else:
					i -= 1
			urradii.append(np.max(row)-row[i])
		ucradii = []
		for col in self.centcols:
			tracker = 0
			i = np.argmax(col)
			while tracker ==0:
				if col[i+1]>col[i]:
					tracker = 1
				else:
					i -= 1
			ucradii.append(np.max(col)-col[i])
		return urradii, ucradii

	def radii(self):
		lrradii, lcradii = self.lower_radii()
		urradii, ucradii = self.upper_radii()
		return [(lrradii[i]+lcradii[i]+urradii[i]+ucradii[i])/4 for i in range(len(lrradii))]

	def statistics(self):
		return np.mean(self.radii), np.mean(self.amps), np.std(self.radii), np.std(self.amps)

	def filter_data(self):
		init_amps, init_radii = [x for x in self.amps if (x > self.avg_amp - 2*self.std_amp)], [x for x in self.radii if (x > self.avg_radius - 2*self.std_radius)]
		return [x for x in init_amps if (x < self.avg_amp + 2*self.std_amp)], [x for x in init_radii if (x < self.avg_radius + 2*self.std_radius)]

	def filtered_statistics(self):
		return np.mean(self.filtered_radii), np.mean(self.filtered_amps), np.std(self.filtered_radii), np.std(self.filtered_amps)

	def radii_to_mm(self,data):
		return [rad*.0056 for rad in data]

	def amp_to_relbright(self,data):
		return [amp/255 for amp in data]

	def plots(self,filter=True):
		fig, (ax1,ax2) = plt.subplots(2,1,sharex=True)
		ax1.plot(self.xdata,self.amp_to_relbright(self.amps),'o')
		ax2.plot(self.xdata,self.radii_to_mm(self.radii),'o')
		ax1.set_title("Transverse Laser Amplitude and Radius")
		ax2.set_xlabel("Camera Position (mm)")
		ax1.set_ylabel("Relative Brightnesss") #central pixel values normalized to 255
		ax2.set_ylabel("Radius (mm)")
		if filter:
			ax1.set_ylim((self.filt_avg_amp-2*self.filt_std_amp)/255,(self.filt_avg_amp+2*self.filt_std_amp)/255)
			plt.text(0.1,0.8,'$\mu$={:.2f}\n$\sigma$={:.2f}'.format(self.filt_avg_amp/255,self.filt_std_amp/255),ha='center',va='center',transform=ax1.transAxes)
			ax2.set_ylim(.0056*(self.filt_avg_radius-2*self.filt_std_radius),.0056*(self.filt_avg_radius+2*self.filt_std_radius))
			plt.text(0.1,0.8,'$\mu$={:.2f}\n$\sigma$={:.2f}'.format(self.filt_avg_radius*.0056,self.filt_std_radius*.0056),ha='center',va='center',transform=ax2.transAxes)
		else:
			plt.text(0.1,0.8,'$\mu$={:.2f}\n$\sigma$={:.2f}'.format(self.avg_radius*.0056,self.std_radius*.0056),ha='center',va='center',transform=ax2.transAxes)
			plt.text(0.1,0.8,'$\mu$={:.2f}\n$\sigma$={:.2f}'.format(self.avg_amp/255,self.std_amp/255),ha='center',va='center',transform=ax1.transAxes)
		plt.show()

Directory("2018-04-12-spot-data/Test1",20,0)