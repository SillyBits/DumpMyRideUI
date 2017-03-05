###############################
# ProcessorFactory.py
#
# Factory for generating processors based one several criterias:
# - Filename and extension
# - File contents (e.g. header bytes like 'MZ', 'MSCE' or 'MSCF')
###############################

import sys
import os

from processors.FolderProcessor		import FolderProcessor
from processors.PlainProcessor		import PlainProcessor
from processors.ZipProcessor		import ZipProcessor
from processors.CabProcessor		import CabProcessor
from processors.SwfProcessor 		import SwfProcessor
#from processors.?Processor 		import ?Processor


'''
More processors to come:
- Images, returning photo widget instead
- Video??
- ...
'''
 

###############################
# Main factory class
###############################

class ProcessorFactory:

	@staticmethod
	def create(file):
		assert file

		if not os.path.exists(file):
			return None

		if os.path.isdir(file):
			return FolderProcessor(file)

		path,filename = os.path.split(file)
		name,ext = os.path.splitext(filename)
		ext = ext.lower()
		
		if ext == ".zip":
			return ZipProcessor(file)
		
		if ext == ".cab":
			return CabProcessor(file)
			# There are two different processors based on magic, "MSCF" and "MSCE", 
			# first must use "cabextract" whereas latter is avail as code already.
			#header = str(ProcessorFactory._load(file,4), encoding="utf-8")
			#if header == "MSCF": return CabProcessor(file)
			#if header == "MSCE": return CabCEProcessor(file)

		if ext == ".swf":
			return SwfProcessor(file)

		if ext == ".lst": # e.g. 'autoinstall.lst' which contains info for executing installation
			return PlainProcessor(file)

		# More processors to come ...

		# No match, so do a hex dump but no details
		return PlainProcessor(file,True,False)


	@staticmethod
	def _load(file, maxbytes=-1):
		if not os.path.exists(file):
			print("ProcessoryFactory._load: File '{}' doesn't exist".format(file))
			return None
		f = open(file, "rb", 0)
		if not f:
			print("ProcessoryFactory._load: Error opening file '{}'".format(file))
			return None
		content = f.read(maxbytes)
		f.close()
		return content
