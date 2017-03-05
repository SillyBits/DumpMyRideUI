from tkinter import *
import tkinter as tk

#import ui.UIHelpers
from ui.UIHelpers import ModalDialog


class AboutDialog(ModalDialog):

    def __init__(self, parent):
        super().__init__(parent, padx=20, pady=20)

    def create_widgets(self, parent):
        self.title = "About DumpMyRide"
        with open("README.md", "rt") as file:
            s = file.read()
            ttk.Label(parent, text=s).pack(side=TOP, fill=BOTH, expand=Y)
