import os, sys

inFile = open(sys.argv[1],'r')
oFile = open(sys.argv[1].replace(".tsv",".csv"),'w')
for line in inFile:
	oFile.write(line.replace("\t",","))
inFile.close()
oFile.close()
