# User interface helpers
#

import sys
import os
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


#
# A simple modal dialog template
#
class ModalDialog:

	def __init__(self, parent, width=None, height=None, padx=10, pady=10):
		self.dlg = Toplevel(parent, padx=padx, pady=pady)
		self.dlg.withdraw()

		self.create_widgets(self.dlg)
		ttk.Button(self.dlg, text="Ok", command=self.on_ok).pack(side="bottom")

		if not width and not height:
			self.dlg.update()
			width = self.dlg.winfo_width()
			height = self.dlg.winfo_height()
		x = parent.winfo_x() + (parent.winfo_width() - width)>>1
		y = parent.winfo_y() + (parent.winfo_height() - height)>>1
		self.dlg.geometry("{}x{}+{}+{}".format(width,height,x,y))
		self.dlg.resizable(False, False)

		self.dlg.deiconify()
		self.dlg.transient(parent)
		self.dlg.grab_set()
		parent.wait_window(self.dlg)

	def create_widgets(self, parent):
		raise NotImplementedError

	def on_ok(self):
		self.dlg.destroy()


#
# Auto-hiding scrollbars
# (based on http://effbot.org/zone/tkinter-autoscrollbar.htm)
#
class AutohideScrollbar(ttk.Scrollbar):

	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			self.grid_remove()
		else:
			self.grid()
		super().set(lo, hi)

	def pack(self, **kw):
		raise TclError("cannot use pack with this widget")

	def place(self, **kw):
		raise TclError("cannot use place with this widget")


#
# Wrapper for adding scrollbars to widgets
#
class ScrollableWidget(ttk.Frame):

	def __init__(self, parent):
		super().__init__(parent)
		
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=0)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=0)

		self.content = self.create_widgets(self)
		self.content.grid(row=0, column=0, sticky=NSEW)

		self.vscroll = AutohideScrollbar(self, orient=VERTICAL, command=self.content.yview)
		self.vscroll.grid(row=0, column=1, sticky=(N,S,E))
		self.content["yscrollcommand"] = self.vscroll.set

		self.hscroll = AutohideScrollbar(self, orient=HORIZONTAL, command=self.content.xview)
		self.hscroll.grid(row=1, column=0, sticky=(S,E,W))
		self.content["xscrollcommand"] = self.hscroll.set

	def create_widgets(self, parent):
		raise NotImplementedError

	@property
	def widget(self):
		return self.content


#
# Wrapper around text widget with scrollbars and easy getter/setter for its content
#
class ScrollableText(ScrollableWidget):

	def __init__(self, parent, text=None, disabled=False):
		self.can_be_disabled = disabled
		super().__init__(parent)
		if text: 
			self.set(text)

	def create_widgets(self, parent):
		return tk.Text(parent, wrap=tk.NONE)

	def disable(self):
		if self.can_be_disabled:
			self.content["state"] = "disabled"
		return self

	def enable(self):
		if self.can_be_disabled:
			self.content["state"] = "normal"
		return self

	def show_disabled(self):
		self.enable()
		self.content["bg"] = "#ddd"
		return self.disable()

	def show_enabled(self):
		self.enable()
		self.content["bg"] = "#fff"
		return self.disable()

	def clear(self, from_="1.0", to_=tk.END):
		return self.enable()._delete(from_, to_).disable()

	def set(self, text, tags=None):
		return self.clear().insert("1.0", text, tags)

	def insert(self, pos, text, tags=None):
		return self.enable()._insert(pos, text, tags).disable()

	def get(self, from_="1.0", to_="end"):
		return self.content.get(from_, to_)

	@property
	def no_of_lines(self):
		return int(self.content.index('end-1c').split('.')[0])

	def _insert(self, pos, text, tags):
		curr_pos = self.no_of_lines
		self.content.insert(pos, text, tags)
		self.content.see("{}.0+1l".format(curr_pos) if pos == "end" else pos)
		return self

	def _delete(self, from_, to_):
		self.content.delete(from_, to_)
		return self
