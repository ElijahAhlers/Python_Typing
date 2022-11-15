from kivy.uix.textinput import TextInput


class NoBackspaceEntry(TextInput):

    def __init__(self, disable_backspace=False, **kwargs):
        self.disable_backspace = disable_backspace
        super().__init__(**kwargs)

    def do_backspace(self, from_undo=False, mode='bkspc'):
        if not self.disable_backspace:
            return super(NoBackspaceEntry, self).do_backspace(from_undo, mode)
