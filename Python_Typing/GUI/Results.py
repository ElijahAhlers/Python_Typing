# Python Standard Library
from datetime import date

# Kivy stuff
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock

# Stuff we made
from csv_object import csv_object


class ResultsScreen(Screen):

    seconds_of_down_time = 15
    delay_for_space_bar = 1
    time = 0 - seconds_of_down_time

    name = 'Results'
    redo_button = False
    idle_time = 0
    keyboard = None
    worst_lesson = None
    clock = None
    total_idle_time = 0
    accuracy = 0
    wpm = 0

    def populate(self):
        pass

    def update(self):
        self.keyboard = Window.request_keyboard(None, self, 'string')
        self.keyboard.bind(on_key_down=self.pressed_letter)
        self.clock = Clock.schedule_interval(self.update_time, 1)

        self.time = 0-self.seconds_of_down_time
        self.idle_time = 0

        results = self.manager.results_object.today_results
        self.accuracy = round(sum([x['accuracy'] for x in results]) // len(results), 0)
        self.wpm = round(sum([x['wpm'] for x in results]) // len(results), 1)

        self.redo_button = len(results) == len(self.manager.lesson.lesson_list)
        if self.redo_button:
            self.ids.nextLessonButton.text = 'Redo Yellow Part'
            worst = 0
            worst_acc = 100
            worst_wpm = 1000
            for i, result in enumerate(self.manager.results_object.today_results):
                if result['accuracy'] <= worst_acc:
                    if result['wpm'] < worst_wpm:
                        worst = i
                        worst_acc = result['accuracy']
                        worst_wpm = result['wpm']
            self.worst_lesson = worst

        data = []
        for i, result in enumerate(self.manager.results_object.today_results):
            data += [{
                'name': result['name'],
                'accuracy': '{:0>2}'.format(result['accuracy']),
                'wpm': '{:0>3}'.format(result['wpm']),
                'redo_button': self.redo_button,
                'color': (0, .5, 1, 1) if i != self.worst_lesson else (1, 1, 0, 1),
                'screen': self
                }]

        self.ids.lesson_results.data = data
        self.ids.averageaccuracy.text = str(self.accuracy)+'%'
        self.ids.averagewpm.text = str(self.wpm)
        self.ids.idletime.text = '{:0>2}:{:0>2}'.format(self.total_idle_time // 60, self.total_idle_time % 60)
        self.ids.timeUntilIdleTime.text = '{}{:0>2}:{:0>2}'.format('-' if self.time < 0 else '',
                                                                   abs(self.time) // 60,
                                                                   abs(self.time) % 60)

    def update_time(self, *args):
        self.time += 1
        if self.time > 0:
            self.total_idle_time += 1
        self.ids.idletime.text = '{:0>2}:{:0>2}'.format(self.total_idle_time // 60, self.total_idle_time % 60)
        self.ids.timeUntilIdleTime.text = '{}{:0>2}:{:0>2}'.format('-' if self.time < 0 else '',
                                                                   abs(self.time) // 60,
                                                                   abs(self.time) % 60)

    def pressed_letter(self, keyboard, ascii_tuple, letter, modifiers):
        if letter == ' ' and self.time > (0 - self.seconds_of_down_time + self.delay_for_space_bar):
            self.next_lesson()

    def next_lesson(self):
        if not self.redo_button:
            self.manager.next_lesson = len(self.manager.results_object.today_results)
        else:
            self.manager.next_lesson = self.worst_lesson
        self.finish_up()

    def redo_lesson(self, name):
        self.manager.next_lesson = next(
            i for i, item in enumerate(self.manager.results_object.today_results) if item['name'] == name)
        self.finish_up()

    def finish_up(self):
        self.clock.cancel()
        self.keyboard.unbind(on_key_down=self.pressed_letter)
        self.manager.results_object.totalResultsIdleTime += self.idle_time
        self.manager.results_object.totalIdleTime += self.idle_time
        self.manager.get_screen('Typing').start_lesson()
        self.manager.current = 'Typing'

    def exit(self):
        self.clock.cancel()
        self.keyboard.unbind(on_key_down=self.pressed_letter)
        self.manager.results_object.totalIdleTime += self.idle_time
        self.manager.results_object.totalResultsIdleTime += self.idle_time
        self.manager.results_object.record_results()
        self.manager.current = 'Lesson Select'
        Window.fullscreen = False
