# Built into python
import os

# Kivy stuff
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

# Stuff we made
import Logic.CSVFuncs as ce
from Logic.LessonClass import Day as MakeDay
from Logic.Results import Results

Window.borderless = True


def find_next_lesson(yesterday_lesson):
    lesson_list = ce.readCSVFile(str(open('Save Location.txt').read()) + '/TypingFiles/LessonList.csv')
    today_lesson = 0
    for i in range(len(lesson_list)):
        if lesson_list[i]['Name'] == yesterday_lesson:
            today_lesson = i + 1
            break
        else:
            pass
    return lesson_list[today_lesson]['Name']


def find_lesson(lesson):
    lesson_list = ce.readCSVFile(str(open('Save Location.txt').read()) + '/TypingFiles/LessonList.csv')
    lesson_num = 0
    for i in range(len(lesson_list)):
        if lesson_list[i]['Name'] == lesson:
            lesson_num = i
            break
        else:
            pass
    return lesson_list[lesson_num]['Location'], lesson_list[lesson_num]['Name']


class HomeWindow(Screen):

    def __init__(self, user, **kwargs):
        self.user = user
        Builder.load_file('KivyGraphicFiles/TypingHome.kv')
        super(HomeWindow, self).__init__(**kwargs)
        self.name = 'LessonSelectScreen'
        self.fill_in_lessons()
        self.fill_in_stats()

    def fill_in_lessons(self):
        raw_data = ce.readCSVFile(open('Save Location.txt').read() + 'TypingFiles/LessonList.csv')
        self.ids.selectable_lessons.data = [
            {
                'text': '{}: {}'.format(day['Number'], day['Name']),
                'location': day['Location'],
                'lesson_number': day['Number'].split(' ')[-1],
                'name': day['Name'],
                'screen': self
            }
            for day in raw_data]

    def fill_in_stats(self):
        path = open('Save Location.txt').read() + 'UserData/' + self.user.username + '/history.csv'
        if os.path.exists(path):
            all_file_history = ce.readCSVFile(path)
            self.ids.lastlesson.text = 'Last time, you typed ' + str(all_file_history[-1]['Lesson'])
            self.ids.accuracy.text = str(all_file_history[-1]['Accuracy'] + '%')
            self.ids.wpm.text = str(all_file_history[-1]['WPM'])
            self.ids.idleTime.text = str(all_file_history[-1]['Idle Time'])

            if all_file_history[-1]['Lesson'] != 'TestyThingamabob':
                self.ids.nextlesson.text = find_next_lesson(all_file_history[-1]['Lesson'])
                self.ids.nextlesson.location, self.ids.nextlesson.name = find_lesson(self.ids.nextlesson.text)
            else:
                self.ids.nextlesson.text = 'TestyThingamabob'
                self.ids.nextlesson.location, self.ids.nextlesson.name = find_lesson('TestyThingamabob')

    def select_lesson(self, selected_button):
        new_day = MakeDay(selected_button.name, selected_button.location)
        self.manager.day = new_day
        self.manager.resultsObject = Results(new_day, self.manager.user)
        self.manager.nextLesson = 0
        self.manager.lesson = self.manager.day.lesson_list[self.manager.nextLesson]
        self.manager.current = 'TypingWindow'
        self.manager.get_screen('TypingWindow').start_lesson()

    def change_password(self):
        self.manager.current = 'Change Password'

    def games(self):
        self.manager.current = 'Games Menu'
        Window.fullscreen = 'auto'

    def typing_history(self):
        self.manager.current = 'TypingHistory'
