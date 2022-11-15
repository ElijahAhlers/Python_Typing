# Kivy Stuff
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

# Stuff we made
from Logic.CSVFuncs import readCSVFile


class TypingHistory(Screen):
    
    def __init__(self, user, **kwargs):
        self.username = user.username
        Builder.load_file('KivyGraphicFiles/TypingHistory.kv')
        super().__init__(**kwargs)
        self.name = 'TypingHistory'
        self.insert_results()
        self.ids.name.text = 'History - ' + self.username

    def exit(self):
        self.manager.current = 'LessonSelectScreen'

    def insert_results(self):
        all_data = readCSVFile(str(open('Save Location.txt').read()) + 'UserData/' + self.username + '/history.csv')
        for dic in all_data:
            dic['lesson'] = dic.pop('Lesson')
            dic['accuracy'] = dic.pop('Accuracy')
            dic['wpm'] = dic.pop('WPM')
            dic['idle_time'] = dic.pop('Idle Time')
        all_data.sort(key=lambda x: x['Date'])
        self.ids.lesson_results.data = all_data
            
