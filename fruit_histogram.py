import os, sys, time
from datetime import timedelta
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

class FruitHistogram:
	def __init__(self, file_name):
		# initialize IO files and global variables
		self.inFile = open(file_name,'r')
		self.by_name = defaultdict(int)
		self.by_color = defaultdict(int)


    	def __del__(self):
		# close all open files in destruct
		self.inFile.close()


	def execution_time(func): # timer decorator
		def wrapper(*args, **kwargs):
			begin = time.time()
			func(*args, **kwargs)
			finish = time.time()
			time_in_sec = finish - begin
			print 'Excecution time:', str(timedelta(seconds=time_in_sec))
		return wrapper


    	@execution_time
	def process(self):
		for line in self.inFile:
			if line.startswith("#") or line.startswith("fruit"): #skip header lines
				continue
			data = line.strip().split("\t")
			if len(data) < 3: #skip insufficient lines
				continue
			fruit = data[0]
			color = data[1]
			quantity = int(data[2])

			# increase quantity by name
			self.incName(fruit, quantity)

			# increase quantity by color
			self.incColor(color, quantity)

		self.printColorCounts()
		self.printPlots()


	def incName(self, fruit, quantity):
		self.by_name[fruit] += quantity


	def incColor(self, color, quantity):
		self.by_color[color] += quantity

		
	def printPlots(self):
		plot_index = []
		plot_list = []
		for i in self.by_color:
			plot_index.append(i)
			plot_list.append(self.by_color[i])

		index = np.arange(len(plot_index))
		bar_width = 0.3
		rects1 = plt.bar(index, plot_list, bar_width, align='center', color='b')

		plt.xlabel('Color')
		plt.ylabel('Quantity')
		plt.title('histogram by color')
		plt.xticks(index + bar_width / 2 - 0.13, plot_index)
		plt.show()
        plt.close()


	def printColorCounts(self):
		print "quantity by color"
		for i in self.by_color:
			print i, ":", self.by_color[i]

if __name__ == "__main__":
	help_message = \
	"""
	*********************************************************
	* This script requires one argument                     *
	* usage : fruit_histogram.py <input_file>               *
	*********************************************************
	"""
	# print help
	if len(sys.argv) < 2 or \
		"-h" in sys.argv or \
		"-H" in sys.argv or \
		"--help" in sys.argv or \
		"--HELP" in sys.argv:
		print help_message
		exit()

	# get IO file names from args
	file_name = sys.argv[1]

	# init instance and run driver functions
	FruitHistogram_obj = FruitHistogram(file_name)
	FruitHistogram_obj.process()
	del FruitHistogram_obj

