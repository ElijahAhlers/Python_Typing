# Kivy Stuff
from kivy.uix.screenmanager import Screen

# Stuff we made
from csv_object import csv_object


class HistoryScreen(Screen):
    name = 'History'

    def populate(self):
        self.ids.name.text = 'History - ' + self.manager.user.username
        return
        with csv_object(f'{self.manager.save_location}/User_History/{self.manager.user.username}.csv') as file:
            all_data = file.body
        for dic in all_data:
            dic['number'] = dic.pop('Part')
            dic['accuracy'] = dic.pop('Accuracy')
            dic['wpm'] = dic.pop('WPM')
            dic['idle_time'] = dic.pop('Idle Time')
        all_data.sort(key=lambda x: x['Date'])
        self.ids.lesson_results.data = all_data

    def exit(self):
        self.manager.current = 'Part Select'
