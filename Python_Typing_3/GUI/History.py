# Kivy Stuff
from kivy.uix.screenmanager import Screen

# Stuff we made
from csv_object import csv_object


class HistoryScreen(Screen):
    name = 'History'

    def populate(self):
        self.ids.name.text = 'History - ' + self.manager.user.username

        with csv_object(f'{self.manager.save_location}UserData/{self.manager.user.username}/history.csv') as file:
            all_data = file.body
        for dic in all_data:
            dic['lesson'] = dic.pop('Lesson')
            dic['accuracy'] = dic.pop('Accuracy')
            dic['wpm'] = dic.pop('WPM')
            dic['idle_time'] = dic.pop('Idle Time')
        all_data.sort(key=lambda x: x['Date'])
        self.ids.lesson_results.data = all_data

    def exit(self):
        self.manager.current = 'Lesson Select'

            
