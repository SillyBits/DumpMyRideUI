###############################
# DumpMyRideUI.py
#
# Dumping info from SyncII (MFT) installation images
###############################

import sys
import os

from tkinter import *
import tkinter as tk
from tkinter import ttk #@Reimport
from tkinter import font
from tkinter import filedialog

from Options import Options
from Nodes import Nodes, Node
from ui.UIHelpers import ModalDialog, ScrollableText
from ui.ContentTree import ContentTree
from ui.AboutDialog import AboutDialog
from ui.OptionsDialog import OptionsDialog

import zipfile
from processors.ProcessorFactory import ProcessorFactory
from processors.ZipProcessor import ZipProcessor


###############################
# Globals
###############################

_options = None


###############################
# Application
###############################

class Application(ttk.Frame):

	extract_to = None # If empty, will extract to path ZIP is located, else to relative path
	nodes = None


	def __init__(self, master=None):
		super().__init__(master, name="dumpmyrideui")
		self.pack(fill=BOTH, expand=Y)
		self.master.title(self.get_title())
		self.master.minsize(640,480)
		self.columnconfigure(0, weight=1, minsize=400)
		self.rowconfigure(0, weight=1, minsize=300)
		self.create_widgets()
		# Finally, update UI
		self.update_extract_location()
		self.update_ui()
		self.update_tree()


	'''
	UI generation
	'''

	def create_widgets(self):
		self.main = ttk.Frame(self)
		self.main.pack(side=TOP, fill=BOTH, expand=Y)
		self.main.columnconfigure(0, weight=1, minsize=400)
		self.main.grid(row=0, column=0, sticky=NSEW)
		self.create_menubar(self.main)
		self.create_toolbars(self.main)
		self.create_content(self.main)
		self.create_statusbar(self.main)

	def create_menubar(self, parent):
		self.menubar = Menu(parent)

		self.menu_file = Menu(self.menubar)
		self.menubar.add_cascade(menu=self.menu_file, label='File')
		self.menu_file.add_command(label='Open root ...', command=self.fileOpenRoot)
		self.menu_file.add_command(label='Close root', command=self.fileCloseRoot)
		self.menu_file.add_separator()
		self.menu_file.add_command(label='Extract selected', command=self.fileExtractSelected)
		self.menu_file.add_command(label='Extract all', command=self.fileExtractAll)
		self.menu_file.add_separator()
		self.menu_file.add_command(label='Options', command=self.fileOptions)
		self.menu_file.add_separator()
		self.menu_file.add_command(label='Exit', command=self.fileExit)

		self.menu_help = Menu(self.menubar)
		self.menubar.add_cascade(menu=self.menu_help, label='Help')
		self.menu_help.add_command(label='About ...', command=self.helpAbout)

		self.master['menu'] = self.menubar

	def create_toolbars(self, parent):
		#self.main.rowconfigure(0, weight=0, minsize=0)
		return

	def create_statusbar(self, parent):
		self.statusbar = ttk.Frame(parent)
		self.statusbar["borderwidth"] = 2
		self.statusbar["relief"] = "sunken"
		self.statusbar["padding"] = 1
		parent.rowconfigure(999, weight=0, minsize=15)
		self.statusbar.rowconfigure(0, weight=1, minsize=15)
		self.statusbar.columnconfigure(0, weight=1, minsize=180)
		self.statusbar.columnconfigure(1, weight=0, minsize=400)
		self.statusbar.columnconfigure(999, weight=0, minsize=15)
		self.statusbar.grid(row=999, column=0, sticky=(N,S,E,W))

		self.statustext = ttk.Label(self.statusbar, text="Ready ...")
		self.statustext.grid(column=0, row=0, sticky=NSEW)

		self.progressbar = None

		ttk.Sizegrip(self.statusbar).grid(column=999, row=0, sticky=(S,E))

	def create_content(self, parent):
		self.panes = ttk.Panedwindow(parent, orient=HORIZONTAL)
		self.panes.pack(side=TOP, fill=BOTH, expand=Y)
		parent.rowconfigure(1, weight=1, minsize=300)
		self.panes.grid(row=1, column=0, sticky=NSEW)

		self.tree = ContentTree(self.panes, popup=self.tree_popup, \
								selchange=self.tree_selchange, \
								expanding=self.tree_expanding)
		self.nodes = Nodes(self.tree)

		self.content = ttk.Notebook(self.panes)
		self.details = ScrollableText(self.content, "", True)
		self.details_tab = 0
		self.content.add(self.details, text="Details")
		self.hexdump = ScrollableText(self.content, "", True)
		self.hexdump_tab = 1
		self.content.add(self.hexdump, text="Hex dump")

		self.panes.add(self.tree)
		self.panes.add(self.content)


	'''
	Updates UI
	'''

	def update_ui(self):
		self.master.title(self.get_title())
		#TODO: Be more precise on menu item states
		#      e.g. archives not yet extracted will need this option to be avail
		cab_avail = "normal" if _options.cabinet else "disabled"
		self.menu_file.entryconfigure("Extract selected", state=cab_avail)
		self.menu_file.entryconfigure("Extract all", state=cab_avail)
		self.menu_file.entryconfigure("Close root", state=cab_avail)
		#self.update_tree() # only called when _options.cabinet has changed!
		# more to come, e.g. populating tree, ...
		#...
		self.set_statusbar()
		Tk.update_idletasks(self)

	def update_tree(self):
		self.tree.clear()
		if not _options.cabinet or not os.path.exists(_options.cabinet):
			return
		if not zipfile.is_zipfile(_options.cabinet):
			print("Given file isn't a valid ZIP")
			return
		# more tests to follow, e.g. '.cab' needs explicit handling

		print("\nBuilding tree ...")
		last_selection = _options.last_selection
		self.app_busy()
		self.show_progress_bar(animate=True)
		node = self.nodes.add(None, _options.cabinet, "Root", "Main installation file",
								self.extract_to,
								details=None, hexdump=None, lazy=False, callback=None)
		self.set_statusbar()
		self.hide_progress_bar()
		self.app_ready()
		if last_selection:
			if not last_selection in self.nodes:
				#TODO: Build tree until last_selection reached
				a=""
			else:
				self.tree.focus(last_selection, force=True)
		else:
			self.tree.focus(node.label, force=True)
			_options.last_selection = node.label
		'''
		vals = { "label":"Root", "info":"Main installation file", "exists":None, \
				"processor":ZipProcessor(_options.cabinet), "extract_to":self.extract_to }
		last_selection = _options.last_selection
		iid = self.tree.add("", vals["label"], vals["info"], vals["exists"], open=True)
		self.values = { iid:vals }
		self.tree_populate(iid, open=True, init_progress=True)
		print("... done building")
		if last_selection:
			if not last_selection in self.values:
				#TODO: Build tree until last_selection reached
				a=""
			else:
				self.tree.focus(last_selection, force=True)
		else:
			self.tree.focus(vals["label"], force=True)
			_options.last_selection = vals["label"]
		#self.hexdump.show_disabled()
		#self.details.show_disabled()
		'''


	'''
	Tree handling
	'''

	values = {} # => Nodes
	tree_popup_menu = None

	def tree_popup(self, event, iid):
		if not iid:
			return
		node = self.nodes[iid]
		print("\nTree requested popup menu @ {}/{}:".\
			format(event.x_root,event.y_root),"\n-",iid,"->",node)
		if not self.tree_popup_menu:
			self.tree_popup_menu = Menu(self)
			self.tree_popup_menu.add_command(label='Extract selected', command=self.fileExtractSelected)
			self.tree_popup_menu.add_command(label='Extract all', command=self.fileExtractAll)
		#TODO: Be more precise on menu item states
		#      e.g. archives not yet extracted will need this option to be avail
		avail = True
		#avail = (not vals["exists"]) and (vals["processor"] is ZipProcessor or vals["processor"] is CabProcessor)
		#avail = (not vals["exists"]) or (vals["processor"] and vals["processor"].can_save)
		avail = "normal" if avail else "disabled"
		self.tree_popup_menu.entryconfigure("Extract selected", state=avail)
		self.tree_popup_menu.post(event.x_root,event.y_root)

	def tree_selchange(self, event, iid):
		if not iid:
			return
		_options.last_selection = iid
		node = self.nodes[iid]
		print("\nTree selection changed:\n-",iid,"->",node)
		self.set_statusbar("Working on '{}' ...".format(node.label))
		self.show_progress_bar(animate=True)
		self.hexdump.set(node.get_hexdump()).show_disabled()
		self.details.set(node.get_details()).show_disabled()
		'''
		if node.exists == False:
			msg = "No data to display, file needs to be extracted first"
			self.hexdump.set(msg).show_disabled()
			self.details.set(msg).show_disabled()
		elif node.label == "Root":
			self.hexdump.set("").show_disabled()
			self.details.set("This is your main installation file").show_disabled()
		else:
			def callback():
				self.update_progress_bar()
			processor = node.processor
			if processor:
				print("- Processor:",processor)
				if processor.has_hexdump:
					self.hexdump.set(processor.get_hexdump(callback)).show_enabled()
					self.content.select(self.hexdump_tab)
				else:
					self.hexdump.set("No hex dump avail for this type of file").show_disabled()
				if processor.has_details:
					self.details.set(processor.get_details(callback)).show_enabled()
					self.content.select(self.details_tab)
				else:
					self.details.set("No details avail for this type of file").show_disabled()
			else:
				self.hexdump.set("").show_disabled()
				self.details.set("").show_disabled()
		'''
		self.set_statusbar(None)
		self.hide_progress_bar()
		Tk.update(self)

	def tree_expanding(self, event, iid):
		if not iid:
			return
		node = self.nodes[iid]
		print("\nTree expanding:\n-",iid,"->",node)
		self.nodes.expand(iid)
		'''
		childs = self.tree.childs(iid)
		print("  -",childs)
		if len(childs) == 1 and childs[0].endswith("/dummy"):
			self.tree.delete(childs)
			self.tree_populate(iid, True, True, 1)
		'''

	def tree_populate(self, iid, open=False, init_progress=False, max_levels=None):
		if not iid:
			return

		vals = self.values[iid]
		self.set_statusbar("Working on '{}' ...".format(vals["label"]))
		if init_progress:
			self.app_busy()
			self.show_progress_bar(animate=True)

		try:
			processor = vals["processor"]
			if not processor:
				return

			# Get childs ...
			def callback():
				self.update_progress_bar()
				#Tk.update_idletasks(self)
			content = processor.get_childs(callback) or {}
			if not len(content):
				return

			# ... and fill tree
			print(content,"\n")
			if max_levels:
				max_levels += iid.count("/")

			def recurs_fill(curr, parent, vals, open):
				print(parent,">>",self.prettify_values(vals))

				file = os.path.join(vals["extract_to"],vals["label"])
				depth = parent.count("/")+1

				#if max_levels and depth > max_levels:
				#	if os.path.isdir(file):
				#		dummy = self.tree.add(parent, "dummy", "dummy", None)
				#	return

				if not "processor" in vals:
					filename,ext = os.path.splitext(vals["label"])
					is_archive = ext.lower() in (".zip",".cab")

					vals["processor"] = ProcessorFactory.create(file)
					if is_archive:
						vals["info"] = "(Archive)"
						vals["extract_to"] = os.path.join(vals["extract_to"],filename)
					else:
						vals["info"] = "(File)" if os.path.isfile(file) \
								else "(Folder)" if os.path.isdir(file) \
								else "?"
						vals["extract_to"] = file
					vals["exists"] = os.path.exists(file)#vals["extract_to"])

					new_parent = self.tree.add(parent, vals["label"], vals["info"], vals["exists"], depth<2)
					self.values[new_parent] = vals

					if is_archive and vals["exists"]:
						# Process archive contents
						#self.tree_populate(new_parent, False)
						# Delayed until knot gets expanded, so we do add a
						# fake which gets replaced when expanded
						dummy = self.tree.add(new_parent, "dummy", "dummy", None)

					parent = new_parent

				# Non-path childs first
				for file in sorted( [key for key in curr.keys() if len(curr[key]) == 0] ):
					print("- File:",file)
					new_vals = { "label":file, "extract_to":vals["extract_to"] }
					recurs_fill(curr[file], parent, new_vals, depth<2)
				# Paths second
				for path in sorted( [key for key in curr.keys() if len(curr[key]) > 0] ):
					print("- Path:",path)
					new_vals = { "label":path, "extract_to":vals["extract_to"] }
					recurs_fill(curr[path], parent, new_vals, depth<2)

			recurs_fill(content["\\"], iid, vals, open)
			#'''
		finally:
			if init_progress:
				self.set_statusbar()
				self.hide_progress_bar()
				self.app_ready()

		'''
		try:
			def callback():
				self.update_progress_bar()
				#Tk.update_idletasks(self)
			processor = vals["processor"]
			if not processor:
				return
			# Process processor contents
			content = processor.get_childs(callback) or {}
			if not len(content):
				return
			# ... and fill tree
			def check_existance(path, file):
				if not os.path.exists(path):
					return (False,None)
				info = None
				location = None
				name,ext = os.path.splitext(file)
				ext = ext.lower()
				if ext == ".zip" or ext == ".cab":
					info = "(Archive)"
					location = name
				else:
					name += ext
				return (os.path.exists(os.path.join(path,name)),info,location)
			def recurs_fill(curr, extract_path, parent, filename, info, exists, open, skip_this=False):
				callback()
				#print("-",filename,"@",extract_path)
				print("-",self.shorten_path(extract_path))
				self.set_statusbar(extract_path)
				if not skip_this:
					iid = parent + "/" + filename
					#if not iid in self.values:
					processor = ProcessorFactory.create(extract_path)
					#if info == "zip" or info == "cab":
					#	extract_path = extract_path[:-(len(info)+1)]
					#	info = "(Archive)"
					iid = self.tree.add(parent, filename, info, exists, open)
					self.values[iid] = { "label":filename, "info":info, "exists":exists, "processor":processor, \
										"path":os.path.join(self.values[parent]["path"],filename), "extract_to":extract_path }
					parent = iid
				for key in sorted(curr.keys()):
					if len(curr[key]) > 0: continue # Non-branches first
					curr_path = os.path.join(extract_path,key)
					exists,info,location = check_existance(extract_path,key)
					if not info: info = "(File)"
					iid = recurs_fill(curr[key], curr_path, parent, key, info, exists, open)
				for key in sorted(curr.keys()):
					if len(curr[key]) == 0: continue # Branches second
					curr_path = os.path.join(extract_path,key)
					exists,info,location = check_existance(extract_path,key)
					iid = recurs_fill(curr[key], curr_path, parent, key, info, exists, open)

			if not open and iid in self.values:
				self.tree.widget.item(iid, open=False)
			recurs_fill(content["\\"], vals["extract_to"], iid, vals["label"], vals["info"], vals["exists"], open, True)
		finally:
			self.set_statusbar()
			self.hide_progress_bar()
		'''


	'''
	Menu handlers
	'''

	def fileOpenRoot(self):
		new_file = filedialog.askopenfilename(title="Select SyncMyRide root file", filetypes=[("Containers",".zip .cab")], defaultextension=".zip")
		if len(new_file) > 0:
			_options.last_selection = None
			_options.current_marker = None
			_options.cabinet = new_file
			self.update_extract_location()
			self.update_ui()
			self.update_tree()

	def fileCloseRoot(self):
		_options.last_selection = None
		_options.current_marker = None
		_options.cabinet = None
		self.extract_to = None
		self.update_ui()
		self.update_tree()

	def fileExtractSelected(self):
		raise Exception(__name__ + " needs new implementation")
		'''
		values = self.values[self.tree.current]
		print("\nThis will extract selected item only: {}\n{}".\
			format(self.tree.current,self.prettify_values(values)))
		processor = values["processor"]
		if processor and processor.can_save:
			processor.save(values["extract_to"], callback=self.extract_callback)
			#self.update_ui()
			self.tree_populate(self.tree.current)
		'''

	def fileExtractAll(self):
		raise Exception(__name__ + " needs new implementation")
		'''
		print("\nThis will extract all contents from {}".\
			format(os.path.basename(_options.cabinet)))
		values = self.values[os.path.basename(_options.cabinet)]
		processor = values["processor"]
		if processor and processor.can_save:
			#processor.save(vals["extract_to"], callback=self.extract_callback)
			#TODO: call childs
			self.update_ui()
		'''

	def fileOptions(self):
		dlg = OptionsDialog(self.master, _options)
		if dlg.changed:
			#TODO: Save changes
			self.update_ui()

	def fileExit(self):
		self.master.destroy()

	def helpAbout(self):
		AboutDialog(self.master)


	'''
	Progress bar handling
	'''

	def show_progress_bar(self, max_=100, animate=False):
		self.hide_progress_bar()
		self.progressbar = ttk.Progressbar(self.statusbar, orient=HORIZONTAL,
							length=200, mode=("indeterminate" if animate else "determinate"), maximum=max_)
		self.progressbar.grid(column=1, row=0, sticky=NSEW)
		if animate:
			self.progressbar.start(100)
		Tk.update_idletasks(self)

	def hide_progress_bar(self):
		if self.progressbar:
			self.progressbar.destroy()
		self.progressbar = None
		Tk.update_idletasks(self)

	def update_progress_bar(self, pos=None):
		if self.progressbar:
			if pos:
				self.progressbar.step(pos)
			else:
				self.progressbar.step()
		Tk.update_idletasks(self)


	'''
	Status bar handling
	'''

	def set_statusbar(self, text=None):
		self.statustext["text"] = text or "Ready ..."
		Tk.update_idletasks(self)


	'''
	Mouse cursor handling
	'''

	def app_busy(self):
		self._mouse("wait")

	def app_ready(self):
		self._mouse("")

	def _mouse(self, cursor):
		root.config(cursor=cursor)
		Tk.update(root)


	'''
	Helpers
	'''

	def get_title(self):
		s = "DumpMyRide"
		if _options.cabinet:
			s += " - " + os.path.basename(_options.cabinet)
		return s

	def update_extract_location(self):
		if not _options.cabinet:
			self.extract_to = None
			return
		subdir = _options.extract_location
		if "%filename%" in subdir:
			subdir = subdir.replace("%filename%", os.path.splitext(os.path.basename(_options.cabinet))[0])
		self.extract_to = os.path.join(os.path.dirname(_options.cabinet), subdir)
		print("Will use following extract location:\n    " + self.extract_to)

	def extract_callback(self, type, info=None):
		if type == "archive_start": # info: No. of files to be extracted
			self.set_statusbar("Starting extraction ...")
			self.show_progress_bar(max_=info+1)
			Tk.update_idletasks(self)
			return
		if type == "archive_end": # info: Success-flag
			self.set_statusbar("Done extracting")
			self.hide_progress_bar()
			Tk.update_idletasks(self)
			return
		if type == "file_start": # info: File being extracted (relative path)
			self.set_statusbar("Extracting {} ...".format(info))
			self.update_progress_bar()
			Tk.update_idletasks(self)
			return
		if type == "file_end": # info: File extracted (relative path)
			'''
			=> MUST be dealt with in another place as we're lacking info on 'parent'
			while info.endswith("/"): info = info[:-1]
			while info.endswith("\\"): info = info[:-1]
			iid = os.path.basename(_options.cabinet) + "/" + info
			if iid in self.values:
				file = os.path.join(self.extract_to,info)
				self.tree.update_image(iid, os.path.exists(file))
			if not self.values[iid]["processor"]:
				self.values[iid]["processor"] = ProcessorFactory.create(file)
				#print("  => ", self.values[iid]["processor"])
				if self.values[iid]["processor"] and self.values[iid]["processor"].can_save:
					#TODO: Build subtree
					todo = ""
			'''
			Tk.update_idletasks(self)




'''
Main
'''

_options = Options("DumpMyRideUI.ini")

root = tk.Tk()
root.option_add('*tearOff', FALSE)

#TODO: Use _options to position to previously used position
if _options.geometry.lower() == "zoomed":
	root.wm_state("zoomed")
else:
	root.geometry(_options.geometry)

app = Application(master=root)
app.mainloop()

#TODO: Get geometry before window is being destroyed. But how?
'''
if root.wm_state() == "zoomed":
	_options.geometry = "zoomed"
else:
	_options.geometry = root.geometry()
'''

_options.save()

sys.exit(0)
