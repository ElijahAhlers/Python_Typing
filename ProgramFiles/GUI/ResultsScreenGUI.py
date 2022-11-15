# Python Standard Library
from os.path import exists as file_exists
import threading as thread
import time as perf
from datetime import date
import logging

# Kivy stuff
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock

# Stuff we made
from Logic.FindWorstFile import *
import Logic.CSVFuncs as ce

Builder.load_file('KivyGraphicFiles/ResultsScreenGUI.kv')
Window.borderless = False


class ResultsWindow(Screen):

    secondsofdowntime = 15
    delayforspacebar = 1
    time = 0-secondsofdowntime

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'ResultsWindow'
        self.redo_button = False
        self.idleTimeOnThisScreen = 0
        self.keyboard = None
        self.worst_lesson = None
        self.clock = None
        self.idleTime = 0
        self.accuracy = 0
        self.wpm = 0

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
        results = self.manager.resultsObject.todaysResults
        self.accuracy = round(sum([x['accuracy'] for x in results]) // len(results), 0)
        self.wpm = round(sum([x['wpm'] for x in results]) // len(results), 1)
        self.ids.averageaccuracy.text = str(self.accuracy)+'%'
        self.ids.averagewpm.text = str(self.wpm)
        self.redo_button = len(results) == len(self.manager.day.lessonlist)
        if self.redo_button:
            self.ids.nextLessonButton.text = 'Redo Yellow Lesson'
            worst = 0
            worst_acc = 100
            worst_wpm = 1000
            for i, result in enumerate(self.manager.resultsObject.todaysResults):
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
        for i, result in enumerate(self.manager.resultsObject.todaysResults):
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

        path = self.manager.location+'/UserData/'+self.manager.user.username+'/history.csv'
        if file_exists(path):
            ce.writeToCSVFile(
                path,
                [{
                    'Date': date.today().strftime("%m/%d/%y"),
                    'Lesson': self.manager.day.lessonName,
                    'Accuracy': round(self.accuracy, 0),
                    'WPM': round(self.wpm, 0),
                    'Idle Time': self.idleTime
                }])
        else:
            ce.writeNewCSVFile(
                path,
                ['Date', 'Lesson', 'Accuracy', 'WPM', 'Idle Time'],
                [{
                    'Date': date.today().strftime("%m/%d/%y"),
                    'Lesson': self.lessonName,
                    'Accuracy': round(self.averageAccuracy, 0),
                    'WPM': round(self.averageWPM, 0),
                    'Idle Time': self.idleTime
                }])
        self.manager.resultsObject.recordReslus()
    
    def exit(self):
        self.clock.cancel()
        self.keyboard.unbind(on_key_down=self.pressed_letter)
        self.manager.resultsObject.totalIdleTime += self.idleTimeOnThisScreen
        self.manager.resultsObject.totalResultsIdleTime += self.idleTimeOnThisScreen
        self.recordFinalResults()
        self.manager.current = 'LessonSelectScreen'
        Window.fullscreen = False

    def nextLesson(self):
        if not self.redo_button:
            self.manager.nextLesson = len(self.manager.resultsObject.todaysResults)
        else:
            self.manager.nextLesson = self.worst_lesson
        self.finish_up()

    def redo_lesson(self, name):
        self.manager.nextLesson = next(
            i for i, item in enumerate(self.manager.resultsObject.todaysResults) if item['name'] == name)
        self.finish_up()

    def finish_up(self):
        self.clock.cancel()
        self.keyboard.unbind(on_key_down=self.pressed_letter)
        self.manager.resultsObject.totalResultsIdleTime += self.idleTimeOnThisScreen
        self.manager.resultsObject.totalIdleTime += self.idleTimeOnThisScreen
        self.manager.lesson = self.manager.day.lessonlist[self.manager.nextLesson]
        self.manager.get_screen('TypingWindow').start_lesson()
        self.manager.current = 'TypingWindow'

        
