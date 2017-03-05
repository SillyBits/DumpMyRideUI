###############################
# SwfProcessor.py
#
# Shockwave flash file processor
###############################

import sys
import os

from processors.ProcessorBase import ProcessorBase

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


###############################
# Main processor class
###############################

class SwfProcessor(ProcessorBase):

	def __init__(self, file):
		super().__init__(file)
		self.parser = createParser(self.file)
		if not self.parser:
			print("Unable to parse file '{}'".format(self.file))

	@property
	def description(self):
		return "Shockwave flash"

	@property
	def has_childs(self): 
		return True
	def get_childs(self, callback=None): 
		if not self.parser:
			return None
		tree = { "\\": {} }
		'''
		cab = None
		try:
			cab = pymspack.CabFile(self.file)
			infos = cab.infolist()
			for info in infos:
				if callback: callback()
				parts = info.filename.split("\\") if "\\" in info.filename \
						else info.filename.split("/") if "/" in info.filename \
						else None
				if not parts:
					tree["\\"][info.filename] = {}
				else:
					parts = [x for x in parts if x!=""]
					curr = tree["\\"]
					for part in parts:
						if callback: callback()
						if not part in curr:
							curr[part] = {}
						curr = curr[part]
		except:
			print("Failure reading file '{}':\n".format(self.file), sys.exc_info())
			tree = {}
		finally:
			if cab:
				cab.close()
		'''
		return tree

	@property
	def has_details(self):
		return self.parser != None
	def get_details(self, callback=None):
		if not self.parser:
			return None
		try:
			if callback: callback()
			metadata = extractMetadata(self.parser, 1) #1=Best quality
			if callback: callback()
		except Exception as err:
			return "Metadata extraction error:\n" + err
		if not metadata:
			return "Unable to extract metadata"
		return "\n".join(metadata.exportPlaintext())
		'''
signature : FWS
-  <class 'hachoir.field.integer.integerFactory.<locals>.Integer'> 	version : 10
-  <class 'hachoir.field.integer.integerFactory.<locals>.Integer'> 	filesize : 348248
-  <class 'hachoir.parser.container.swf.RECT'> 						rect : None					xmin, xmax, ymin, ymax
-  <class 'hachoir.parser.container.swf.FixedFloat16'> 				frame_rate : 15.0
-  <class 'hachoir.field.integer.integerFactory.<locals>.Integer'> 	frame_count : 1
		'''
		'''		
		content = ""
		for line in metadata.exportPlaintext():
			if callback: callback()
			if line[0] != "-" and content != "":
				content += "\n"
			content += line + "\n"
		return content
		'''

	@property
	def can_save(self): 
		return False #True
	def save(self, path, callback=None):
		return False
		'''
		#path = os.path.join(os.path.dirname(path),"_TEMP")
		print("Extracting file '{}' to '{}':".format(self.file,path))
		if not os.path.exists(path): 
			try:
				os.mkdir(path, 0o777)
			except:
				print("Error creating directory '{}'\n".format(path),sys.exc_info())
				return False
		success = True
		cab = None
		try:
			cab = pymspack.CabFile(self.file)
			infos = cab.infolist()
			if callback: callback("archive_start", len(infos))
			for info in infos:
				print("-", info.filename)
				try:
					if callback: callback("file_start", info.filename)
					cab.extract(info.filename, info.filename, path)
					if callback: callback("file_end", info.filename)
				except:
					print("Failure extracting file '{}' to '{}':\n".format(info.filename,os.path.join(path,info.filename)), sys.exc_info())
					success = False
		except:
			print("Failure reading file '{}':\n".format(self.file), sys.exc_info())
			return False
		finally:
			#os.chdir(curr_dir)
			if cab:
				cab.close()
		if callback: callback("archive_end", success)
		return success
		'''
