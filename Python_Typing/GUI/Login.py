# Kivy stuff
from kivy.uix.screenmanager import Screen

# Stuff we made
from csv_object import csv_object

import os
import hashlib
from dataclasses import dataclass, field


@dataclass
class User:
    username: str
    path_to_data: str
    first_name: str = None
    last_name: str = None
    hashed_password: str = None
    registered: bool = None
    admin: bool = None

    def __post_init__(self):
        with csv_object(f'{self.path_to_data}/UserData/user_data.csv') as usernames_file:
            print(usernames_file.filename)
            print(usernames_file.body)
            try:
                index = [entry['username'] for entry in usernames_file.body].index(self.username)
                self.first_name = usernames_file.body[index]['first_name']
                self.last_name = usernames_file.body[index]['last_name']
                self.hashed_password = usernames_file.body[index]['password']
                self.registered = bool(int(usernames_file.body[index]['registered']))
                self.admin = bool(int(usernames_file.body[index]['admin']))
            except IndexError:
                pass

    def check_password(self, password):
        return self.hashed_password == hashlib.sha256(password.encode('utf-8')).hexdigest()


class LoginScreen(Screen):
    name = 'Login'

    def populate(self):
        self.ids.username.text = str(os.getlogin())
        self.ids.notifyupdate.text = 'Software version:\nYes, you are indeed\nrunning software'

    def ExitButton(self):
        self.get_root_window().close()
        
    def Authenticate(self):
        user = User(self.ids.username.text.lower(), self.manager.save_location)
        print(user)
        if user.check_password(self.ids.password.text):
            self.manager.user = user
            print('successful login')
            return
            self.manager.populate()
            self.manager.current = 'Lesson Select'
            return
        self.ids.incpass.text = 'Incorrect Username\nor Password'
        self.ids.incpass.color = 1, 0, 0, 1

    def cheatyFunc(self):
        self.ids.username.text = 'debugme'
        self.ids.password.text = 'test'
        self.Authenticate()
