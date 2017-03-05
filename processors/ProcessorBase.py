###############################
# ProcessorBase.py
#
# Basic processor
###############################

import sys
import os


###############################
# Basic processor
###############################

class ProcessorBase:

	def __init__(self, file):
		self.file = file


	@property
	def description(self):
		raise NotImplementedError


	#
	# Actions avail with processor
	#

	@property
	def has_childs(self): 
		return False
	def get_childs(self, callback=None): 
		raise NotImplementedError #return None

	@property
	def has_hexdump(self): 
		return False
	def get_hexdump(self, callback=None): 
		raise NotImplementedError #return ""

	@property
	def has_details(self): 
		return False
	def get_details(self, callback=None): 
		raise NotImplementedError #return ""

	@property
	def can_save(self): 
		return False
	def save(self, path, callback=None):
		raise NotImplementedError #return False


	#
	# Basic methods avail to all processors
	#

	def load(self, callback=None):
		if callback: callback()
		if not os.path.exists(self.file):
			print("{}: File '{}' doesn't exist".format(self.__name__,self.file))
			return None
		f = open(self.file, "rb", 0)
		if not f:
			print("{}: Error opening file '{}'".format(self.__name__,self.file))
			return None
		if callback: callback()
		data = f.readall()
		if callback: callback()
		f.close()
		return data


	#
	# Private methods avail to all processors
	#
	
	def _create_hexdump(self, data, start=0, length=-1, linelength=16, callback=None):
		dump = ""
		if length <= 0: length = len(data)
		#lines = int(length / linelength)
		#fragment = length % linelength
		#if fragment > 0:
		#	lines += 1
		lines = int((length+linelength-1) / linelength)
		l = 0
		while l < lines:
			if callback: callback()
			p = start + (l * linelength)
			addr = self._tohex(p,8)
			by = " "
			d = " "
			i = 0
			while i < linelength:
				if p < (start+length):
					val = data[p]
					by += " " + self._tohex(val,2)
					d += chr(val) if val >= 32 and val < 128 else "."
				else:
					by += "   "
					d += " "
				i += 1
				p += 1
				if i % 4 == 0: by += " "
			l += 1
			#s = addr + " " + by + " " + d
			#if l < lines: print(s)
			#else: sys.stdout.write(s)
			dump += addr + " " + by + " " + d + "\n"
		return dump

	def _tohex(self,val,length=2):
		s = hex(val).upper()[2:]
		return ("0000000000000000" + s)[-length:]
