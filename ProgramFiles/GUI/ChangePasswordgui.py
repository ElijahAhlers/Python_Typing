#Kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

#Our Stuff
from Logic.CSVFuncs import writeNewCSVFile as wnCSV
from Logic.CSVFuncs import readCSVFile as rCSV

#Python
import hashlib

Window.borderless = True

class firstLogin(GridLayout):
    Builder.load_file('KivyGraphicFiles/firstLogin.kv')
    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        self.locationOfDataFiles = open('Save Location.txt').read()
        self.alldata = rCSV(self.locationOfDataFiles+'UserData/UsernameAndPasswordHashed.csv')
        
    def changePassword(self):
        count = 0
        for person in self.alldata:
            if person['Username'] == self.user.username:
                registered = person['Registered']
                self.alldata.pop(count)
                break
            count+=1
        newdata = {'Username':self.user.username,'Password':hashlib.sha256(str(self.ids.newPassword.text).encode('utf-8')).hexdigest(),'Registered':registered}
        self.alldata.insert(count,newdata)
        wnCSV(self.locationOfDataFiles+'UserData/UsernameAndPassword.csv',['Username','Password','Registered'],self.alldata)
        self.parent.parent.current = 'LessonSelectScreen'

    def verifyData(self):
        oldPasswordCorrect = False
        passwordsMatch = False
        for person in self.alldata:
            if person['Username'] == self.user.username:
                if hashlib.sha256(str(self.ids.oldPassword.text).encode('utf-8')).hexdigest() == person['Password']:
                    oldPasswordCorrect = True
                else:
                    self.ids.whatWentWrong.text = 'Old password is incorrect'
        if self.ids.newPassword.text == self.ids.confirmNewPassword.text:
            passwordsMatch = True
        else:
            self.ids.whatWentWrong.text = 'Passwords do not match'
        if oldPasswordCorrect and passwordsMatch:
            self.changePassword()
