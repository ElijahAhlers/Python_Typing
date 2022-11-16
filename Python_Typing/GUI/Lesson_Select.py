# Built into python
import os
from dataclasses import dataclass, field
from datetime import date, datetime

# Kivy stuff
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen

# Stuff we made
from GUI.Login import User
from csv_object import csv_object


@dataclass
class Part:
    text: str
    backspace: bool
    forced100: bool
    time: int
    name: str
    number: int


@dataclass
class Lesson:
    name: str
    location: str
    save_location: str
    lesson_list: list = field(default_factory=list)
    part_number: int = 0

    def __post_init__(self):
        with csv_object(f'{self.save_location}/TypingFiles/Lessons/{self.location}.csv') as lesson_locations:
            files = lesson_locations.body
        for lesson in files:
            self.lesson_list += [Part(
                open(f"{self.save_location}/TypingFiles/LessonParts/{lesson['Part']}.txt").read(),
                bool(int(lesson['Backspace'])),
                bool(int(lesson['Forced100'])),
                int(lesson['Time']),
                lesson['Part'],
                int(lesson['Number'])
            )]
        self.numOfLessons = len(self.lesson_list)


@dataclass
class Results:
    lesson: Lesson
    user: User
    result_destination: str
    today_results: list = field(default_factory=list)
    totalFileIdleTime: int = 0
    totalResultsIdleTime: int = 0
    totalIdleTime: int = 0

    def add_new_result(self, part, accuracy, wpm, idle_time):
        with csv_object(self.user.history_folder+'/Part_History.csv') as file:
            file.header = ['Date', 'Time', 'Lesson', 'Part', 'Accuracy', 'WPM', 'Idle_Time']
            file.body += [{
                'Date': date.today().strftime("%m-%d-%y"),
                'Time': int((datetime.now() - datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)).total_seconds()),
                'Lesson': self.lesson.name,
                'Part': part.name,
                'Accuracy': accuracy,
                'WPM': wpm,
                'Idle_Time': idle_time
            }]
        result = {
            'name': part.name,
            'accuracy': accuracy,
            'wpm': wpm
        }
        try:
            lesson_index = [x['name'] for x in self.today_results].index(part.name)
            if accuracy >= self.today_results[lesson_index]['accuracy']:
                if wpm >= self.today_results[lesson_index]['wpm']:
                    self.today_results[lesson_index] = result
        except ValueError:
            self.today_results += [result]

    def record_results(self):
        today_date = date.today().strftime('%d-%m-%y')
        today_time = int((datetime.now() - datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        today_accuracy = round(sum([x['accuracy'] for x in self.today_results]) / len(self.today_results), 0)
        today_wpm = round(sum([x['wpm'] for x in self.today_results]) / len(self.today_results), 0)
        file = f'{self.result_destination}/Grading/{self.lesson.name}.csv'
        new_data = [{'last name': self.user.last_name,
                     'first name': self.user.first_name,
                     'date': today_date,
                     'accuracy': today_accuracy,
                     'wpm': today_wpm,
                     'idle time in number': self.totalFileIdleTime,
                     'idle time in results screen': self.totalResultsIdleTime,
                     'total idle time': self.totalIdleTime}]

        with csv_object(file) as results_file:
            try:
                index = [(i['last name'], i['first name']) for i in results_file.body].index((self.user.last_name, self.user.first_name))
                result = results_file.body[index]
                if (float(result['accuracy']) > today_accuracy) or (
                        float(result['accuracy']) == today_accuracy and float(result['wpm']) < today_wpm):
                    results_file.body[index] = new_data
            except ValueError:
                if self.user.registered:
                    results_file.header = ['last name', 'first name', 'date', 'accuracy', 'wpm', 'idle time in number',
                                           'idle time in results screen', 'total idle time']
                    with csv_object(self.result_destination + '/user_data.csv') as usernames_file:
                        for user in usernames_file.body:
                            if user['registered'] == '1' and user['username'] != self.user.username:
                                results_file.body += [{
                                    'last name': user['last_name'],
                                    'first name': user['first_name'],
                                    'date': 0,
                                    'accuracy': 0,
                                    'wpm': 0,
                                    'idle time in number': 0,
                                    'idle time in results screen': 0,
                                    'total idle time': 0
                                }]
                    results_file.body += new_data
                    results_file.body.sort(key=lambda x: (x['last name'], x['first name']))
                    print(results_file.body)
        with csv_object(self.user.history_folder+'/Lesson_History.csv') as lesson_history:
            lesson_history.header = ['date', 'time', 'number', 'accuracy', 'wpm', 'idle_time']
            lesson_history.body += [{
                'date': today_date,
                'time': today_time,
                'number': self.lesson.name,
                'accuracy': today_accuracy,
                'wpm': today_wpm,
                'idle_time': self.totalIdleTime
            }]


class LessonSelectScreen(Screen):
    name = 'Part Select'

    def populate(self):
        with csv_object(f'{self.manager.save_location}/TypingFiles/LessonList.csv') as raw_data:
            self.ids.selectable_lessons.data = [
                {
                    'text': '{}: {}'.format(day['Number'], day['Name']),
                    'location': day['Location'],
                    'lesson_number': day['Number'].split(' ')[-1],
                    'name': day['Name'],
                    'screen': self
                }
                for day in raw_data.body]
        return
        path = f'{self.manager.user.history_folder}/Lesson_History.csv'
        with csv_object(path) as file:
            if file.body:
                self.ids.lastlesson.text = f"Last time, you typed {file.body[-1]['Lesson']}"
                self.ids.accuracy.text = f"{file.body[-1]['Accuracy']}%"
                self.ids.wpm.text = str(file.body[-1]['WPM'])
                self.ids.total_idle_time.text = str(file.body[-1]['Idle Time'])

                with csv_object(f'{self.manager.save_location}/TypingFiles/LessonList.csv') as lesson_list_file:
                    if file.body[-1]['Part'] != 'TestyThingamabob':
                        try:
                            index = [x['Name'] for x in lesson_list_file.body].index(file.body[-1]['Lesson']) + 1
                            self.ids.nextlesson.text = self.ids.nextlesson.name = lesson_list_file.body[index]['Name']
                            self.ids.nextlesson.location = lesson_list_file.body[index]['Location']
                        except ValueError or IndexError:
                            pass
                    else:
                        test_lesson_index = [x['Name'] for x in lesson_list_file.body].index('TestyThingamabob')
                        self.ids.nextlesson.text = self.ids.nextlesson.name = 'TestyThingamabob'
                        self.ids.nextlesson.location = lesson_list_file.body[test_lesson_index]['Location']

    def select_lesson(self, selected_button):
        new_lesson = Lesson(selected_button.name, selected_button.location, self.manager.save_location)
        self.manager.lesson = new_lesson
        self.manager.results_object = Results(new_lesson, self.manager.user, self.manager.save_location)
        self.manager.next_lesson = 0
        self.manager.current = 'Typing'
        self.manager.get_screen('Typing').start_lesson()

    def change_password(self):
        self.manager.current = 'Change Password'

    def games(self):
        self.manager.current = 'Games Menu Manager'
        #Window.fullscreen = 'auto'

    def typing_history(self):
        self.manager.current = 'History'
