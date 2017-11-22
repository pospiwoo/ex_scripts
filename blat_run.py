import os, sys, time
from datetime import timedelta
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

class BLATRun:
	def __init__(self, in_file, seq_file, target_file, mute_blat, win_size):
		# initialize IO files and global variables
		self.win_size = win_size
		self.blat_cmd = ""
		self.seq_file = seq_file
		self.target_file = target_file
		self.out_psl_file = seq_file.replace(".fa",".psl")
		self.mute_blat = mute_blat
		self.inFile = open(in_file,'r')
		self.oFile = open(seq_file,'w')
		self.map_start = 78090747
		self.map_end = 78093312+win_size
		self.map_cov = []
		for i in xrange(self.map_end - self.map_start):
			self.map_cov.append(0)
		self.map_cov_filtered = []
		for i in xrange(self.map_end - self.map_start):
			self.map_cov_filtered.append(0.0)
		self.reads_cnt = 0
		self.in_range_cnt = 0
		self.h_flag = True
		self.cur_blocks = []
		self.cur_block_sizes = []
		self.t_start = 0
		self.t_end = 0


    	def __del__(self): # close all open files in destruct		
		self.inFile.close()
		self.oFile.close()


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
		self.convertToFASTA()
		if not self.mute_blat:
			self.runBLAT()
		self.processPSL()


	def convertToFASTA(self):
		for line in self.inFile:
			if line.startswith("@"):
				header = line
				seq = self.inFile.next()
				strand = self.inFile.next()
				score = self.inFile.next()
				self.oFile.write(header.replace("@",">"))
				self.oFile.write(seq)


	def runBLAT(self):
		self.blat_cmd = ""
		self.blat_cmd += "./blat "
		self.blat_cmd += self.target_file + " "
		self.blat_cmd += self.seq_file + " "
		self.blat_cmd += self.out_psl_file
		os.system(self.blat_cmd)


	def processPSL(self):
		PSLFile = open(self.out_psl_file,'r')
		for line in PSLFile:			
			if self.isHeader(line):
				continue # ignore headers
			data = line.strip().split("\t")
			if len(data) < 21:
				continue # ignore insufficient lines 
			self.reads_cnt += 1
			if not self.isInRange(data):
				continue # ignore reads out of range of interest

			for i in xrange(len(self.cur_blocks)):
				self.increaseCov(i) # estimate coverage for each mapped fragment

		self.filterPSL()

		print "out of", self.reads_cnt, "reads,", \
			self.in_range_cnt, "are within our range of interest"


	def isHeader(self, line):
		if line.startswith("-------"):
			self.h_flag = False
		if self.h_flag:
			return True
		return False


	def isInRange(self, data):
		self.cur_blocks = data[-1].strip(",").split(",")
		self.cur_block_sizes = data[-3].strip(",").split(",")
		self.t_start = int(data[-6])
		self.t_end = int(data[-5])
		if self.t_start >= self.map_start and self.t_end < self.map_end:		
			self.in_range_cnt += 1
			return True
		return False


	def increaseCov(self, block_idx):
		p_start = int(self.cur_blocks[block_idx]) - self.map_start
		p_len = self.cur_block_sizes[block_idx]
		for i in xrange(len(p_len)):
			self.map_cov[p_start+i] += 1


	def printPlots(self, list_data):
		plt.plot(list_data)
		plt.xlabel('relative base starting from chr17:78090747')
		plt.ylabel('coverage')
		plt.show()
        	plt.close()


	def filterPSL(self):
		for i in xrange(len(self.map_cov)-500):
			for j in xrange(500):
				self.map_cov_filtered[i] += float(self.map_cov[i+j])
			self.map_cov_filtered[i] = self.map_cov_filtered[i] / float(self.win_size)


if __name__ == "__main__":
	help_message = \
	"""
	************************************************************
	* This script requires two arguments                       *
	* usage : blat_run.py <input_file> <target_file> <options> *
	* options:                                                 *
	*  -m : don't run BLAT (parse from previous BLAT result)   *
	************************************************************
	"""
	if len(sys.argv) < 2 or \
		"-h" in sys.argv or \
		"-H" in sys.argv or \
		"--help" in sys.argv or \
		"--HELP" in sys.argv:
		print help_message
		exit()
	
	# get IO file names from args
	file_name = sys.argv[1]
	target_name = sys.argv[2]
	if len(sys.argv) >= 4:
		if sys.argv[3] == "mute" or sys.argv[3] == "-m" or sys.argv[3] == "1":
			mute_blat = True
	else:
			mute_blat = False
	seq_file_name = file_name.replace(".fastq",".fa")
	
	# init instance and run driver functions
	win_size = 500
	BLATRun_obj = BLATRun(file_name, seq_file_name, target_name, mute_blat, win_size)
	BLATRun_obj.process()
	BLATRun_obj.printPlots(BLATRun_obj.map_cov[:-win_size])
	BLATRun_obj.printPlots(BLATRun_obj.map_cov_filtered[:-win_size])
	del BLATRun_obj


