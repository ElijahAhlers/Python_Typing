# Kivy stuff
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.lang import Builder
from kivy.clock import Clock

# Stuff we made
from Logic import CheckLogin as cl
from Logic import UserClass

import os

Builder.load_file('KivyGraphicFiles/LoginMaster.kv')
Window.clearcolor = (0, 0, 0, 0)


class LoginWindow(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'Login Window'

        Clock.schedule_once(self.autofillUsername)
        Clock.schedule_once(self.check_for_updates)

    def autofillUsername(self, *args):
        self.ids.username.text = str(os.getlogin())
    
    def ExitButton(self):
        self.get_root_window().close()
        
    def Authenticate(self):
        username = self.ids.username.text.lower()
        if not cl.CheckCreds(self.ids.username.text.lower(), self.ids.password.text):
            self.ids.incpass.text = 'Incorrect Username\nor Password'
            self.ids.incpass.color = 1, 0, 0, 1
        else:
            self.manager.user = UserClass.User(username)
            self.manager.current = 'LessonSelectScreen'

    def check_for_updates(self, *args):
        self.ids.notifyupdate.text = 'Software version '+str(open('Version.txt').read())
