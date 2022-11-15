#Kivy
from kivy.uix.screenmanager import Screen

#Our Stuff
from csv_object import csv_object

#Python
import hashlib


class ChangePasswordScreen(Screen):
    name = 'Change Password'

    def populate(self):
        pass

    def verify_data(self):
        old_password_correct = False
        passwords_match = False
        with csv_object(self.manager.save_location + 'UserData/UsernameAndPassword.csv') as all_data:
            for person in all_data.body:
                if person['Username'] == self.manager.user.username:
                    if hashlib.sha256(str(self.ids.oldPassword.text).encode('utf-8')).hexdigest() == person['Password']:
                        old_password_correct = True
                    else:
                        self.ids.whatWentWrong.text = 'Old password is incorrect'
        if self.ids.newPassword.text == self.ids.confirmNewPassword.text:
            passwords_match = True
        else:
            self.ids.whatWentWrong.text = 'New passwords do not match'
        if old_password_correct and passwords_match:
            with csv_object(self.manager.save_location + 'UserData/UsernameAndPassword.csv') as auth_file:
                auth_file.body[
                    [entry['Username'] for entry in auth_file.body].index(self.manager.user.username)
                ]['Password'] = hashlib.sha256(str(self.ids.newPassword.text).encode('utf-8')).hexdigest()
            self.go_back_to_lesson_select()

    def go_back_to_lesson_select(self):
        self.manager.current = 'Lesson Select'
