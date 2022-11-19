# Kivy Stuff
from kivy.uix.screenmanager import Screen

# Stuff we made
from csv_object import csv_object


class HistoryScreen(Screen):
    name = 'History'

    def populate(self):
        self.ids.name.text = 'History - ' + self.manager.user.username
        with csv_object(f'{self.manager.user.history_folder}/Lesson_History.csv') as file:
            all_data = file.body
        if all_data:
            all_data.sort(key=lambda x: (x['date'], x['time']))
            self.ids.lesson_results.data = all_data

    def exit(self):
        self.manager.current = 'Lesson Select'
