###############################
# CabCEProcessor.py
#
# WinCE Cab file processor
# NOT USED CURRENTLY!
###############################

import sys
import os

from processors.ProcessorBase import ProcessorBase


###############################
# Main processor class
###############################

class CabCEProcessor(ProcessorBase):

	def __init__(self, file):
		super().__init__(file)

	@property
	def description(self):
		return "Microsoft CE Cabinet"

	@property
	def has_childs(self): 
		return True
	def get_childs(self): 
		'''
		#if not zipfile.is_zipfile(self.file):
		#	print("Given file isn't a valid ZIP")
		#	return None
		tree = { "\\": {} }
		cab = None
		try:
			cab = CabFile(self.file)
			infos = cab.infolist()
			for info in infos:
				parts = info.filename.split("\\") if "\\" in info.filename \
						else info.filename.split("/") if "/" in info.filename \
						else None
				if not parts:
					tree["\\"][info.filename] = {}
				else:
					parts = [x for x in parts if x!=""]
					curr = tree["\\"]
					for part in parts:
						if not part in curr:
							curr[part] = {}
						curr = curr[part]
		except:
			print("Failure reading file '{}':\n".format(self.file), sys.exc_info())
			tree = {}
		finally:
			if cab:
				cab.close()
		return tree
		'''
		return {}

	@property
	def can_save(self): 
		return True
	def save(self, path, callback=None):
		'''
		print("Extracting file '{}' to '{}':".format(self.file,path))
		if not os.path.exists(path): 
			try:
				os.mkdir(path)
			except:
				print("Error creating directory '{}'\n".format(path),sys.exc_info())
				return False
		success = True
		cab = None
		try:
			cab = CabFile(self.file)
			print("_c_cab_decompressor:",cab._c_cab_decompressor,"\n_c_cabd_cabinet:",cab._c_cabd_cabinet)
			infos = cab.infolist()
			if callback: callback("archive_start", len(infos))
			for info in infos:
				print("-", info.filename)
				try:
					if callback: callback("file_start", info.filename)
					cab.extract(info, info.filename, path)
					if callback: callback("file_end", info.filename)
				except:
					print("Failure extracting file '{}' to '{}':\n".format(info.filename,os.path.join(path,info.filename)), sys.exc_info())
					success = False
		except:
			print("Failure reading file '{}':\n".format(self.file), sys.exc_info())
			return False
		finally:
			if cab:
				cab.close()
		if callback: callback("archive_end", success)
		return success
		'''
		return False
