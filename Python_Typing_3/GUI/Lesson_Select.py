# Built into python
import os
from dataclasses import dataclass, field
from datetime import date

# Kivy stuff
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen

# Stuff we made
from GUI.Login import User
from csv_object import csv_object


@dataclass
class Lesson:
    text: str
    backspace: bool
    forced100: bool
    time: int
    filename: str
    part: int


@dataclass
class Day:
    name: str
    location: str
    save_location: str
    files: list = None
    lesson_list: list = field(default_factory=list)

    def __post_init__(self):
        with csv_object(f'{self.save_location}TypingFiles/Lessons/{self.location}.csv') as lesson_locations:
            self.files = lesson_locations.body
        for lesson in self.files:
            part_title = lesson['Lesson']
            self.lesson_list += [Lesson(
                open(f'{self.save_location}TypingFiles/LessonParts/{part_title}.txt').read(),
                bool(int(lesson['Backspace'])),
                bool(int(lesson['Forced100'])),
                int(lesson['Time']),
                part_title,
                int(lesson['Part'])
            )]
        self.numOfLessons = len(self.lesson_list)


@dataclass
class Results:
    day: object
    user: object
    result_destination: str
    today_results: list = field(default_factory=list)
    totalFileIdleTime: int = 0
    totalResultsIdleTime: int = 0
    totalIdleTime: int = 0

    def addResults(self, lesson_name, accuracy, wpm):
        result = {
            'name': lesson_name,
            'accuracy': accuracy,
            'wpm': wpm
        }
        if lesson_name in [x['name'] for x in self.today_results]:
            lesson_index = [x['name'] for x in self.today_results].index(lesson_name)
            if accuracy >= self.today_results[lesson_index]['accuracy']:
                if wpm >= self.today_results[lesson_index]['wpm']:
                    self.today_results[lesson_index] = result
        else:
            self.today_results += [result]

    def record_results(self):
        today_date = date.today().strftime('%Y/%m/%d')
        today_accuracy = round(sum([x['accuracy'] for x in self.today_results]) / len(self.today_results), 0)
        today_wpm = round(sum([x['wpm'] for x in self.today_results]) / len(self.today_results), 0)
        file = self.result_destination + 'CSVToGrade/' + self.day.name + '.csv'

        new_data = [{'last name': self.user.last_name,
                     'first name': self.user.first_name,
                     'date': today_date,
                     'accuracy': today_accuracy,
                     'wpm': today_wpm,
                     'idle time in lesson': self.totalFileIdleTime,
                     'idle time in results screen': self.totalResultsIdleTime,
                     'total idle time': self.totalIdleTime}]

        with csv_object(file) as results_file:
            try:
                index = [(i['last name'], i['first name']) for i in results_file.body].index(
                    (self.user.last_name, self.user.first_name))
                result = results_file.body[index]
                if (
                        float(result['accuracy']) > today_accuracy) or (
                        float(result['accuracy']) == today_accuracy and float(result['wpm']) < today_wpm):
                    results_file.body[index] = new_data
            except ValueError:
                if self.user.registered:
                    with csv_object(self.result_destination + 'UserData/UsernameAndPassword.csv') as usernames_file:
                        registeredUsernames = [i['Username'] for i in usernames_file.body if i['Registered'] == '1']
                    registeredUsernames.remove(self.user.username)
                    results_file.header = ['last name', 'first name', 'date', 'accuracy', 'wpm', 'idle time in lesson',
                                           'idle time in results screen', 'total idle time']
                    results_file.body = [{
                        'last name': User(username, self.result_destination).last_name,
                        'first name': User(username, self.result_destination).first_name,
                        'date': 0,
                        'accuracy': 0,
                        'wpm': 0,
                        'idle time in lesson': 0,
                        'idle time in results screen': 0,
                        'total idle time': 0
                    } for username in registeredUsernames]
                    results_file.body += new_data
                    print(results_file.header)


def find_next_lesson(yesterday_lesson, save_location):
    with csv_object(f'{save_location}/TypingFiles/LessonList.csv') as file:
        lesson_list = file.body
    today_lesson = 0
    for i in range(len(lesson_list)):
        if lesson_list[i]['Name'] == yesterday_lesson:
            today_lesson = i + 1
            break
        else:
            pass
    return lesson_list[today_lesson]['Name']


def find_lesson(lesson, save_location):
    with csv_object(f'{save_location}/TypingFiles/LessonList.csv') as file:
        lesson_list = file.body
    lesson_num = 0
    for i in range(len(lesson_list)):
        if lesson_list[i]['Name'] == lesson:
            lesson_num = i
            break
        else:
            pass
    return lesson_list[lesson_num]['Location'], lesson_list[lesson_num]['Name']


class LessonSelectScreen(Screen):
    name = 'Lesson Select'

    def populate(self):
        with csv_object(f'{self.manager.save_location}TypingFiles/LessonList.csv') as raw_data:
            self.ids.selectable_lessons.data = [
                {
                    'text': '{}: {}'.format(day['Number'], day['Name']),
                    'location': day['Location'],
                    'lesson_number': day['Number'].split(' ')[-1],
                    'name': day['Name'],
                    'screen': self
                }
                for day in raw_data.body]

        path = self.manager.save_location + 'UserData/' + self.manager.user.username + '/history.csv'
        with csv_object(path) as file:
            if file.body:
                all_file_history = file.body
                self.ids.lastlesson.text = 'Last time, you typed ' + str(all_file_history[-1]['Lesson'])
                self.ids.accuracy.text = str(all_file_history[-1]['Accuracy'] + '%')
                self.ids.wpm.text = str(all_file_history[-1]['WPM'])
                self.ids.idleTime.text = str(all_file_history[-1]['Idle Time'])

                if all_file_history[-1]['Lesson'] != 'TestyThingamabob':
                    self.ids.nextlesson.text = find_next_lesson(all_file_history[-1]['Lesson'],self.manager.save_location)
                    self.ids.nextlesson.location, self.ids.nextlesson.name = find_lesson(self.ids.nextlesson.text, self.manager.save_location)
                else:
                    self.ids.nextlesson.text = 'TestyThingamabob'
                    self.ids.nextlesson.location, self.ids.nextlesson.name = find_lesson('TestyThingamabob', self.manager.save_location)

    def select_lesson(self, selected_button):
        new_day = Day(selected_button.name, selected_button.location, self.manager.save_location)
        self.manager.day = new_day
        self.manager.resultsObject = Results(new_day, self.manager.user, self.manager.save_location)
        self.manager.nextLesson = 0
        self.manager.lesson = self.manager.day.lesson_list[self.manager.nextLesson]
        self.manager.current = 'Typing'
        self.manager.get_screen('Typing').start_lesson()

    def change_password(self):
        self.manager.current = 'Change Password'

    def games(self):
        self.manager.current = 'Games Menu Manager'
        Window.fullscreen = 'auto'

    def typing_history(self):
        self.manager.current = 'History'
