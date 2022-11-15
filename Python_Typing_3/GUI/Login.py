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
    registered: bool = None
    history: list = field(default_factory=list)

    def __post_init__(self):
        user_folder = f'{self.path_to_data}UserData'
        with csv_object(f'{user_folder}/{self.username}/history.csv') as history_file:
            self.history = history_file.body
        with csv_object(f'{user_folder}/{self.username}/data.csv') as data_file:
            self.first_name = data_file.body[0]['FirstName']
            self.last_name = data_file.body[0]['LastName']
        with csv_object(f'{user_folder}/UsernameAndPassword.csv') as usernames_file:
            self.registered = self.username in [i['Username'] for i in usernames_file.body]


class LoginScreen(Screen):
    name = 'Login'

    def populate(self):
        self.ids.username.text = str(os.getlogin())
        self.ids.notifyupdate.text = 'Software version:\nYes, you are indeed\nrunning software'

    def ExitButton(self):
        self.get_root_window().close()
        
    def Authenticate(self):
        username = self.ids.username.text.lower()
        with csv_object(self.manager.save_location + 'UserData/UsernameAndPassword.csv') as auth_file:
            auth_usernames = [entry['Username'] for entry in auth_file.body]
            if username in auth_usernames:
                index = auth_usernames.index(username)
                if auth_file.body[index]['Password'] == hashlib.sha256(
                        self.ids.password.text.encode('utf-8')).hexdigest():
                    self.manager.user = User(username, self.manager.save_location)
                    self.manager.populate()
                    self.manager.current = 'Lesson Select'
                    return
        self.ids.incpass.text = 'Incorrect Username\nor Password'
        self.ids.incpass.color = 1, 0, 0, 1

    def cheatyFunc(self):
        self.ids.username.text = 'debugme'
        self.ids.password.text = 'test'
        self.Authenticate()
