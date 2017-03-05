import os

from tkinter import *
import tkinter as tk

import ui.UIHelpers


class ContentTree(ui.UIHelpers.ScrollableWidget):

    def __init__(self, parent, popup=None, selchange=None, expanding=None):
        self.values = {}
        self.popup = popup
        self.selchange = selchange
        self.expanding = expanding
        super().__init__(parent)
        self.font = font.Font(self.widget)
        self.icon_none = tk.PhotoImage(file=os.path.join("resources","treeicon_empty.png"))
        self.icon_exists = tk.PhotoImage(file=os.path.join("resources","treeicon_exists.png"))
        self.icon_missing = tk.PhotoImage(file=os.path.join("resources","treeicon_missing.png"))

    def create_widgets(self, parent):
        tree = ttk.Treeview(parent, columns=("info"), displaycolumns="#all", height=20)
        tree.heading("info", text="Info", anchor="w")
        tree.column("info", stretch=False, minwidth=0, width=100)
        if self.popup:
            tree.bind("<Button-3>", func=self.on_rightclick)
            '''
            if (tree.tk.call('tk', 'windowingsystem')=='aqua'):
                # Mac
                tree.bind('<Button-2>', func=self.on_rightclick)
                tree.bind('<Control-1>', func=self.on_rightclick)
            else:
                # Windows/Linux
                tree.bind('<Button-3>', func=self.on_rightclick)
            '''
        if self.selchange:
            self.curr_selection = None
            tree.bind("<<TreeviewSelect>>", func=self.on_selchange)
        if self.expanding:
            tree.bind('<<TreeviewOpen>>', func=self.on_expanding)
        return tree

    def add(self, parent, label, info="", exists=False, open=False):
        iid = ((parent + "/") if parent else "") + label
        params = { 'text':label, 'open':open }
        image = self._get_image(exists)
        if image: params['image'] = image
        self.widget.insert(parent, "end", iid, **params)
        self.widget.set(iid, "info", info)
        self._resize_columns(iid)
        return iid

    def update(self, iid, label=None, info=None, exists=False):
        params = {}
        if label: params["text"] = label
        image = self._get_image(exists)
        if image: params["image"] = image
        if len(params):
            self.widget.item(iid, **params)
        if info != None:
            self.widget.set(iid, "info", info)
        if label or info:
            self._resize_columns(iid)
        return self

    def update_image(self, iid, exists):
        if exists != None:
            self.widget.item(iid, image=self._get_image(exists))
        #else: # How to remove existing image?
        #    self.widget.item(iid, image=None)
        return self

    def delete(self, iid):
        self.widget.delete(iid)
        return self
        
    def clear(self):
        self.widget.delete(*self.widget.get_children())
        return self

    def childs(self, iid):
        return self.widget.get_children(iid)
        
    @property
    def current(self):
        return self.curr_selection #self.widget.selection()

    def focus(self, iid, force=False):
        if force: self.curr_selection = None
        self.widget.selection_set(iid)
        self.widget.focus(iid)
        return self

    def on_rightclick(self, event):
        iid = self.widget.identify_row(event.y)
        if not iid: return
        if self.curr_selection != iid:
            self.curr_selection = iid # Prevent from sending multiple 'selchange'
            self.widget.selection_set(iid)
            self.widget.focus(iid)
            if self.selchange: self.selchange(event, iid)
        self.popup(event, iid)

    def on_selchange(self, event):
        iid = self.widget.focus()
        if not iid: return
        if self.curr_selection == iid: return
        self.curr_selection = iid
        self.selchange(event, iid)

    def on_expanding(self, event):
        print("on_expanding:",event)
        iid = self.widget.focus()
        if not iid: return
        self.expanding(event, iid)
        #self.expanding(event, self.curr_selection)

    def _get_image(self, exists):
        if exists == None: return None
        return  self.icon_exists if exists else \
                self.icon_missing if exists == False else \
                self.icon_none

    def _resize_columns(self, iid):
        item = self.widget.item(iid)
        # Label
        width = self._measure_text(item["text"])
        width += (16+16) * len(iid.split("/"))
        if width > self.widget.column("#0")["width"]:
            self.widget.column("#0", width=width)
        # Info
        width = self._measure_text(item["values"])
        if width > self.widget.column("info")["width"]:
            self.widget.column("info", width=width)
    
    def _measure_text(self, text):
        return 10 + int((self.font.measure(text)/96.0)*72.0)
