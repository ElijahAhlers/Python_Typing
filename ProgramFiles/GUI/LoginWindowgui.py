#Kivy stuff
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

#Stuff we made
from Logic import CheckLogin as cl
from Logic import UserClass

import os

Builder.load_file('KivyGraphicFiles/LoginMaster.kv')    
Window.borderless = True
Window.clearcolor = (0,0,0,0)

class LoginWindow(GridLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.autofillUsername)

    def autofillUsername(self,*args):
        self.ids.username.text = str(os.getlogin())
        
    def get_rid_of_username(self):
        self.ids.username.text = ''
    
    def ExitButton(self):
        self.get_root_window().close()
        
    def Authenticate(self):
        self.username = self.ids.username.text.lower()
        if not cl.CheckCreds(self.ids.username.text.lower(),self.ids.password.text):
            self.ids.incpass.text = 'Incorrect Username\nor Password'
            self.ids.incpass.color = 1,0,0,1
        else:
            self.parent.parent.activeUser = UserClass.User(self.username)
            self.parent.parent.AddSelectScreen()
            self.parent.parent.current = 'LessonSelectScreen'

    def checkforupdates(self):
        self.ids.notifyupdate.text = 'Software version '+str(open('Version.txt').read())
