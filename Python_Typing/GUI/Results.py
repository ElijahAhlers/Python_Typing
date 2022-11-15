# Python Standard Library
from datetime import date

# Kivy stuff
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock

# Stuff we made
from csv_object import csv_object


class ResultsScreen(Screen):

    secondsofdowntime = 15
    delayforspacebar = 1
    time = 0-secondsofdowntime

    name = 'Results'
    redo_button = False
    idleTimeOnThisScreen = 0
    keyboard = None
    worst_lesson = None
    clock = None
    idleTime = 0
    accuracy = 0
    wpm = 0

    def populate(self):
        pass

    def update_everything(self):
        self.update_screen()
        self.update_results()
        self.keyboard = Window.request_keyboard(None, self, 'string')
        self.keyboard.bind(on_key_down=self.pressed_letter)

    def update_screen(self):
        self.time = 0-self.secondsofdowntime
        self.idleTimeOnThisScreen = 0
        self.ids.idletime.text = '{:0>2}:{:0>2}'.format(self.idleTime // 60, self.idleTime % 60)
        self.ids.timeUntilIdleTime.text = '{}{:0>2}:{:0>2}'.format('-' if self.time < 0 else '',
                                                                   abs(self.time) // 60,
                                                                   abs(self.time) % 60)
        results = self.manager.resultsObject.today_results
        self.accuracy = round(sum([x['accuracy'] for x in results]) // len(results), 0)
        self.wpm = round(sum([x['wpm'] for x in results]) // len(results), 1)
        self.ids.averageaccuracy.text = str(self.accuracy)+'%'
        self.ids.averagewpm.text = str(self.wpm)
        self.redo_button = len(results) == len(self.manager.day.lesson_list)
        if self.redo_button:
            self.ids.nextLessonButton.text = 'Redo Yellow Lesson'
            worst = 0
            worst_acc = 100
            worst_wpm = 1000
            for i, result in enumerate(self.manager.resultsObject.today_results):
                if result['accuracy'] <= worst_acc:
                    if result['wpm'] < worst_wpm:
                        worst = i
                        worst_acc = result['accuracy']
                        worst_wpm = result['wpm']
            self.worst_lesson = worst
        self.clock = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, *args):
        self.time += 1
        if self.time > 0:
            self.idleTime += 1
        self.ids.idletime.text = '{:0>2}:{:0>2}'.format(self.idleTime // 60, self.idleTime % 60)
        self.ids.timeUntilIdleTime.text = '{}{:0>2}:{:0>2}'.format('-' if self.time < 0 else '',
                                                                   abs(self.time) // 60,
                                                                   abs(self.time) % 60)

    def update_results(self):
        data = []
        for i, result in enumerate(self.manager.resultsObject.today_results):
            data += [{
                'name': result['name'],
                'accuracy': '{:0>2}'.format(result['accuracy']),
                'wpm': '{:0>3}'.format(result['wpm']),
                'redo_button': self.redo_button,
                'color': (0, .5, 1, 1) if i != self.worst_lesson else (1, 1, 0, 1),
                'screen': self
                }]
        self.ids.lesson_results.data = data

    def pressed_letter(self, keyboard, ascii_tuple, letter, modifiers):
        if letter == ' ' and self.time > (0 - self.secondsofdowntime + self.delayforspacebar):
            self.nextLesson()

    def recordFinalResults(self):

        path = self.manager.save_location+'/UserData/'+self.manager.user.username+'/history.csv'
        with csv_object(path) as file:
            file.header = ['Date', 'Lesson', 'Accuracy', 'WPM', 'Idle Time']
            file.body = [{
                    'Date': date.today().strftime("%m/%d/%y"),
                    'Lesson': self.manager.day.name,
                    'Accuracy': round(self.accuracy, 0),
                    'WPM': round(self.wpm, 0),
                    'Idle Time': self.idleTime
                }]
        self.manager.resultsObject.record_results()
    
    def exit(self):
        self.clock.cancel()
        self.keyboard.unbind(on_key_down=self.pressed_letter)
        self.manager.resultsObject.totalIdleTime += self.idleTimeOnThisScreen
        self.manager.resultsObject.totalResultsIdleTime += self.idleTimeOnThisScreen
        self.recordFinalResults()
        self.manager.current = 'Lesson Select'
        Window.fullscreen = False

    def nextLesson(self):
        if not self.redo_button:
            self.manager.nextLesson = len(self.manager.resultsObject.today_results)
        else:
            self.manager.nextLesson = self.worst_lesson
        self.finish_up()

    def redo_lesson(self, name):
        self.manager.nextLesson = next(
            i for i, item in enumerate(self.manager.resultsObject.today_results) if item['name'] == name)
        self.finish_up()

    def finish_up(self):
        self.clock.cancel()
        self.keyboard.unbind(on_key_down=self.pressed_letter)
        self.manager.resultsObject.totalResultsIdleTime += self.idleTimeOnThisScreen
        self.manager.resultsObject.totalIdleTime += self.idleTimeOnThisScreen
        self.manager.lesson = self.manager.day.lesson_list[self.manager.nextLesson]
        self.manager.get_screen('Typing').start_lesson()
        self.manager.current = 'Typing'

        
