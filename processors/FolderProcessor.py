###############################
# FolderProcessor.py
#
# Folder processor
# Sort of a stub processor 
###############################

import sys
import os

from processors.ProcessorBase import ProcessorBase


###############################
# Main processor class
###############################

class FolderProcessor(ProcessorBase):

	def __init__(self, file):
		super().__init__(file)

	@property
	def description(self):
		return "Folder"

	@property
	def has_childs(self):
		return True
	def get_childs(self, callback=None):
		return {}
