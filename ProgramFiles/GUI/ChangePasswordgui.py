#Kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

#Our Stuff
from Logic.CSVFuncs import writeNewCSVFile as wnCSV
from Logic.CSVFuncs import readCSVFile as rCSV

#Python
import hashlib

Window.borderless = True


class firstLogin(Screen):

    def __init__(self, user, **kwargs):
        self.user = user
        self.locationOfDataFiles = open('Save Location.txt').read()
        self.all_data = rCSV(self.locationOfDataFiles + 'UserData/UsernameAndPassword.csv')
        Builder.load_file('KivyGraphicFiles/firstLogin.kv')
        super().__init__(**kwargs)
        self.name = 'Change Password'

    def change_password(self):
        count = 0
        for person in self.all_data:
            if person['Username'] == self.user.username:
                registered = person['Registered']
                self.all_data.pop(count)
                break
            count += 1
        new_data = {'Username': self.user.username,
                    'Password': hashlib.sha256(str(self.ids.newPassword.text).encode('utf-8')).hexdigest(),
                    'Registered': registered}
        self.all_data.insert(count, new_data)
        wnCSV(self.locationOfDataFiles + 'UserData/UsernameAndPassword.csv',
              ['Username', 'Password', 'Registered'],
              self.all_data)
        self.manager.current = 'LessonSelectScreen'

    def verify_data(self):
        old_password_correct = False
        passwords_match = False
        for person in self.all_data:
            if person['Username'] == self.user.username:
                if hashlib.sha256(str(self.ids.oldPassword.text).encode('utf-8')).hexdigest() == person['Password']:
                    old_password_correct = True
                else:
                    self.ids.whatWentWrong.text = 'Old password is incorrect'
        if self.ids.newPassword.text == self.ids.confirmNewPassword.text:
            passwords_match = True
        else:
            self.ids.whatWentWrong.text = 'New passwords do not match'
        if old_password_correct and passwords_match:
            self.change_password()

    def go_back_to_lesson_select(self):
        self.manager.current = 'LessonSelectScreen'
