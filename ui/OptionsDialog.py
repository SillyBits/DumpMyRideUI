from ui.UIHelpers import ModalDialog
#import Options


class OptionsDialog(ModalDialog):

    def __init__(self, parent, options):
        self.options = options
        super().__init__(parent, 300, 400)
        
    def create_widgets(self, parent):
        ttk.Label(parent, text="Options will go here ^_^").pack(side=TOP, fill=BOTH, expand=Y)

    @property
    def changed(self):
        return False

    def on_ok(self):
        # Save dialog contents to options instance
        #...
        super().on_ok()
