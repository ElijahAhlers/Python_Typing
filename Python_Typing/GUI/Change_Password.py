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

        if self.manager.user.check_password(self.ids.oldPassword.text):
            old_password_correct = True
        else:
            self.ids.whatWentWrong.text = 'Old password is incorrect'

        if self.ids.newPassword.text == self.ids.confirmNewPassword.text:
            passwords_match = True
        else:
            self.ids.whatWentWrong.text = 'New passwords do not match'

        if old_password_correct and passwords_match:
            with csv_object(f'{self.manager.save_location}/user_data.csv') as auth_file:
                auth_file.body[
                    [entry['username'] for entry in auth_file.body].index(self.manager.user.username)
                ]['password'] = hashlib.sha256(str(self.ids.newPassword.text).encode('utf-8')).hexdigest()
            self.go_back_to_lesson_select()

    def go_back_to_lesson_select(self):
        self.manager.current = 'Lesson Select'
