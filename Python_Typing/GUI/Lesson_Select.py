# Built into python
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
        with csv_object(self.user.history_folder + '/Part_History.csv') as file:
            file.header = ['date', 'time', 'lesson', 'part', 'accuracy', 'wpm', 'idle_time']
            file.body += [{
                'date': date.today().strftime("%m-%d-%y"),
                'time': int((datetime.now() - datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)).total_seconds()),
                'lesson': self.lesson.name,
                'part': part.name,
                'accuracy': accuracy,
                'wpm': wpm,
                'idle_time': idle_time
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
        new_data = {'last name': self.user.last_name,
                    'first name': self.user.first_name,
                    'date': today_date,
                    'accuracy': today_accuracy,
                    'wpm': today_wpm,
                    'idle time in lessons': self.totalFileIdleTime,
                    'idle time in results screen': self.totalResultsIdleTime,
                    'total idle time': self.totalIdleTime}

        with csv_object(file) as results_file:
            try:
                index = [(i['last name'], i['first name']) for i in results_file.body].index(
                    (self.user.last_name, self.user.first_name))
                result = results_file.body[index]
                if (float(result['accuracy']) < today_accuracy) or (
                        float(result['accuracy']) == today_accuracy and float(result['wpm']) < today_wpm):
                    results_file.body[index] = new_data
            except ValueError:
                if self.user.registered:
                    results_file.header = ['last name', 'first name', 'date', 'accuracy', 'wpm', 'idle time in lessons',
                                           'idle time in results screen', 'total idle time']
                    with csv_object(self.result_destination + '/user_data.csv') as usernames_file:
                        usernames_file.body = []
                        for user in usernames_file.body:
                            if user['registered'] == '1' and user['username'] != self.user.username:
                                results_file.body += [{
                                    'last name': user['last_name'],
                                    'first name': user['first_name'],
                                    'date': 0,
                                    'accuracy': 0,
                                    'wpm': 0,
                                    'idle time in lessons': 0,
                                    'idle time in results screen': 0,
                                    'total idle time': 0
                                }]
                    results_file.body += [new_data]
                    results_file.body.sort(key=lambda x: (x['last name'], x['first name']))
        with csv_object(self.user.history_folder + '/Lesson_History.csv') as lesson_history:
            lesson_history.header = ['date', 'time', 'lesson', 'accuracy', 'wpm', 'idle_time']
            lesson_history.body += [{
                'date': today_date,
                'time': today_time,
                'lesson': self.lesson.name,
                'accuracy': today_accuracy,
                'wpm': today_wpm,
                'idle_time': self.totalIdleTime
            }]


class LessonSelectScreen(Screen):
    name = 'Lesson Select'

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
            try:
                with csv_object(f'{self.manager.user.history_folder}/Lesson_History.csv') as lesson_history:
                    if lesson_history.body:
                        self.ids.lastlesson.text = f"Last time, you typed {lesson_history.body[-1]['lesson']}"
                        self.ids.accuracy.text = f"{lesson_history.body[-1]['accuracy']}%"
                        self.ids.wpm.text = str(lesson_history.body[-1]['wpm'])
                        self.ids.idle_time.text = str(lesson_history.body[-1]['idle_time'])

                        lesson_names = [x['Name'] for x in raw_data.body]
                        index = lesson_names.index(lesson_history.body[-1]['lesson'])
                        if lesson_history.body[-1]['lesson'] != 'TestyThingamabob':
                            index += 1
                        self.ids.nextlesson.text = self.ids.nextlesson.name = raw_data.body[index]['Name']
                        self.ids.nextlesson.location = raw_data.body[index]['Location']
            except IndexError:
                self.ids.nextlesson.text = 'Not Available'
                self.ids.next_lesson_begin_button.disabled = True

    def select_lesson(self, selected_button):
        new_lesson = Lesson(selected_button.name, selected_button.location, self.manager.save_location)
        self.manager.lesson = new_lesson
        self.manager.results_object = Results(new_lesson, self.manager.user, self.manager.save_location)
        self.manager.next_lesson = 0
        self.manager.current = 'Typing'
        Window.fullscreen = 'auto'
        self.manager.get_screen('Typing').start_lesson()

    def change_password(self):
        self.manager.current = 'Change Password'

    def games(self):
        self.manager.current = 'Games Menu Manager'
        Window.fullscreen = 'auto'

    def typing_history(self):
        self.manager.current = 'History'
