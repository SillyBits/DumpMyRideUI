###############################
# PlainProcessor.py
#
# Plain file processor
# - Hex and details dump can be configured
###############################

import sys
import os

from processors.ProcessorBase import ProcessorBase


###############################
# Main processor class
###############################

class PlainProcessor(ProcessorBase):

	def __init__(self, file, hex=False, details=True):
		super().__init__(file)
		self.do_hexdump = hex
		self.do_details = details

	@property
	def description(self):
		return "Plain file"

	#@property
	#def has_childs(self): return False
	#def get_childs(self): IMPL(__name__)

	@property
	def has_hexdump(self):
		return self.do_hexdump
	def get_hexdump(self, callback=None):
		if not self.do_hexdump:
			return None
		content = self.load(callback)
		if not content or not len(content):
			return "(empty file)"
		return self._create_hexdump(content)

	@property
	def has_details(self):
		return self.do_details
	def get_details(self, callback=None):
		if not self.do_details:
			return None
		content = self.load(callback)
		if not content or not len(content):
			return "(empty file)"
		return content
