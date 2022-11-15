#Python Standard Library
from os.path import exists as file_exists
import threading as thread
import time as perf
from datetime import date
import logging


#pynput stuff
from pynput import keyboard
from pynput.keyboard import Key as keyModule

#Kivy stuff
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock

#Stuff we made
from Logic.FindWorstFile import *
import Logic.CSVFuncs as ce
from Logic.longestStringFunc import leftJustifyWithSpaces as lj
from Logic.longestStringFunc import addASpaceIfTheNumberIsLessThanTen as addSpace

Builder.load_file('KivyGraphicFiles/ResultsScreenGUI.kv')
Window.borderless = False

class Chart(GridLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
    def redo(self, lesson, files):
        done = True
        if self.done:
            self.parent.parent.determineRedo()
            self.parent.parent.exit(fromRedo = True)
            files = [file[0] for file in files]
            self.parent.parent.parent.parent.resultsObject.addIdleTimeFromResultsWindow(self.parent.parent.idleTimeOnThisScreen)
            self.parent.parent.parent.parent.nextLesson = files.index(lesson[0])
            self.parent.parent.parent.parent.MakeTypingWindow()
            self.parent.parent.parent.parent.current = 'TypingWindow'

class ResultsWindow(BoxLayout):

    secondsofdowntime = 15
    delayforspacebar = 1
    time = 0-secondsofdowntime

    def __init__(self, user, files, idleTime, day, **kwargs):
        self.day = day
        self.redoIsAGo = False
        self.user = user
        self.allTheFiles = files
        self.files = self.sortOutTheFilesNotInTheLesson()
        self.numOfLessons = day.numOfLessons
        self.doneWithAllLessons = True if len(self.files)>=day.numOfLessons else False
        self.lessonName = day.lessonName
        self.lessonNumber = day.lessonNumber
        self.buildChart()
        super().__init__(**kwargs)
        self.idleTime = idleTime
        self.idleTimeOnThisScreen = 0
        self.runclock = True
        #Clock.max_iteration = 20
        Clock.schedule_once(self.setupScreen,-1)
        self.StartKeyLogger()
        self.changeNextLessonButton()
        self.changeLessonName()


    def sortOutTheFilesNotInTheLesson(self):
        filesNamesInTheDay = []
        finalList = []
        for j in self.day.lessonlist:
            filesNamesInTheDay.append(j.filename)
        for i in range(len(self.allTheFiles)):
            if self.allTheFiles[i][0] in filesNamesInTheDay:
                finalList.append(self.allTheFiles[i])
        return finalList
                
        
    def setupScreen(self,clockvar):
        while True:
            try:
                self.ids.idletime.text = str(self.parent.parent.idleTime)
                break
            except:
                perf.sleep(0.01)
        self.children[1].children[0].done = self.doneWithAllLessons
        self.averageResults()
        self.ids.averageaccuracy.text,self.ids.averagewpm.text = str(self.averageAccuracy),str(self.averageWPM)
        self.startClock()
        self.ids.idletime.text = self.formatTime(self.idleTime)
        self.ids.timeUntilIdleTime.text = self.formatTime(self.time)
        
    def startClock(self):
        self.clockThread = thread.Thread(target=self.clockLoop)
        self.clockThread.start()

    def clockLoop(self):
        runClock = True
        self.timeCache = perf.perf_counter()
        while runClock:
            runClock = self.runclock
            perf.sleep(self.timeCache+1-perf.perf_counter())
            self.timeCache = perf.perf_counter()
            self.clockUpdate()

    def stopClock(self):
        self.runclock = False

    def clockUpdate(self):
        self.time += 1
        if self.time > 0:
            self.idleTime+=1
            self.idleTimeOnThisScreen += 1
        self.ids.idletime.text = self.formatTime(self.idleTime)
        self.ids.timeUntilIdleTime.text = self.formatTime(self.time)
        if self.time > 0:
            self.ids.timeUntilIdleTime.color = 1,0,0,1

    def StartKeyLogger(self):
        self.listener = keyboard.Listener(on_press=self.KeyPress)
        self.listener.start()

    def StopKeyLogger(self):
        self.listener.stop()

    def KeyPress(self, key):
        if key in [keyModule.enter, keyModule.space] and self.time > (0-self.secondsofdowntime+self.delayforspacebar):
            self.nextLesson()

    def formatTime(self, sec):
        '''Formats a time in seconds to mm:ss
        Parameters: int
        Returns: str'''
        neg = False if sec >= 0 else True
        sec = abs(sec)
        minutes,seconds = str(sec//60),str(sec%60)
        minutes,seconds = minutes if len(minutes)>1 else '0'+minutes, seconds if len(seconds)>1 else '0'+seconds
        minutes,seconds = minutes if len(minutes)>1 else '00', seconds if len(seconds)>1 else '00'
        time = minutes+':'+seconds
        return '- '+time if neg else time
        
    def buildChart(self):
        bestLessons = bestOfFiles(self.files)
        self.BestLessons = bestLessons
        self.lenofbestlessons = len(bestLessons)
        chart = """
<Chart>:
    rows: {0}
""".format(self.findRows())
        
        for part in range(len(bestLessons)):
            chart+="""
    GridLayout:
        cols: 2
        GridLayout:
            cols: 1
            padding: [20,0,0,0]
            Label:
                text: '{0}'
                text_size: self.size
                halign: 'left'
                valign: 'middle'
                font_size: '30sp'
                color: {1}
        GridLayout:
            cols:4
            
            Label:
                text: '{2}'
                font_size: '30sp'
                color: {1}
                
            Label:
                text: ''
            
            Label:
                text: '{3}'
                font_size: '30sp'
                color: {1}
                
""".format(self.getSpacedNames()[part],((1,1,0,1) if bestLessons[part][0] == worstFile(self.files, forLuke = True) and self.doneWithAllLessons else (1,1,1,1)),bestLessons[part][1],bestLessons[part][2])
            if len(bestLessons) == self.numOfLessons:
                self.redoIsAGo = True
                chart+="""
            GridLayout:
                cols: 3

                Label:
                    text: ''
                    
                GridLayout:
                    rows: 3
                    
                    Label:
                        text: ''
                        
                    Button:
                        on_press: root.redo({0},{1})
                        text: 'Redo'
                        
                    Label:
                        text: ''
                        
                Label:
                    text: ''
""".format(str(self.files[part]), str(self.files))
            else:
                chart+="""
            Label:
                text: ''
"""
            

        for fill in range(10-len(bestLessons)):
            chart+="""
    Label:
        text: ''
"""
            
        while True:
            try:
                kivyfile = open('KivyGraphicFiles/chartgui.kv','w')
                kivyfile.write(chart)
                kivyfile.close()
                Builder.unload_file('KivyGraphicFiles/chartgui.kv')
                Builder.load_file('KivyGraphicFiles/chartgui.kv')
                break
            except:
                logging.info('it got stuck trying to open, write to, close, or load into the builder the chartgui kv file')
                
                
    def determineRedo(self):
        self.parent.parent.doneWithLessons = True if self.doneWithAllLessons else False
        if self.parent.parent.doneWithLessons:
            logging.info('determine redo is true in Results window')

    def getSpacedNames(self):
        theList = []
        for i in range(self.lenofbestlessons):
            theList.append(self.BestLessons[i][0])
        return lj(theList,50)
            
        
    def findRows(self):
        rows = bestOfFiles(self.files)
        rows = len(rows)
        if rows < 10:
            rows = 10
        logging.info(rows)
        return rows
        

    def averageResults(self):
        if not self.doneWithAllLessons:
            accuracies = [float(x) for a,x,b in self.files]
            wpms = [float(x) for a,b,x in self.files]
        else:
            best4 = bestOfFiles(self.files)
            accuracies = [float(x) for a,x,b in best4]
            wpms = [float(x) for a,b,x in best4]
        self.averageAccuracy,self.averageWPM = round(sum(accuracies)/len(accuracies),1),round(sum(wpms)/len(wpms),0)

    def recordFinalResults(self):

        path = self.parent.parent.location+'/UserData/'+self.user.username+'/history.csv'
        if file_exists(path):
            ce.writeToCSVFile(
                path,
                [{
                    'Date':date.today().strftime("%m/%d/%y"),
                    'Lesson':self.lessonName,
                    'Accuracy':round(self.averageAccuracy,0),
                    'WPM':round(self.averageWPM,0),
                    'Idle Time':self.idleTime
                }])
        else:
            ce.writeNewCSVFile(
                path,
                ['Date', 'Lesson', 'Accuracy', 'WPM', 'Idle Time'],
                [{
                    'Date':date.today().strftime("%m/%d/%y"),
                    'Lesson':self.lessonName,
                    'Accuracy':round(self.averageAccuracy,0),
                    'WPM':round(self.averageWPM,0),
                    'Idle Time':self.idleTime
                }])
        self.parent.parent.resultsObject.recordReslus()
    
    def exit(self,fromRedo = False):
        self.StopKeyLogger()
        self.runclock = False

        self.parent.parent.resultsObject.addIdleTimeFromResultsWindow(self.idleTimeOnThisScreen)
        
        self.parent.parent.idleTime = self.idleTime
        logging.info('The Exit Function got called')
        if not fromRedo:
            self.recordFinalResults()
        self.parent.parent.current = 'LessonSelectScreen'
        Window.fullscreen = False
        

    def games(self):
        pass       

    def nextLesson(self):
        self.StopKeyLogger()
        self.runclock = False
        self.determineRedo()
        self.parent.parent.resultsObject.addIdleTimeFromResultsWindow(self.idleTimeOnThisScreen)
        self.parent.parent.idleTime = self.idleTime
        self.parent.parent.nextLesson = len(self.files) if not self.doneWithAllLessons else worstFile(self.files)
        self.parent.parent.MakeTypingWindow()
        self.parent.parent.current = 'TypingWindow'

    def chooseBest(self):
        best = bestOfFiles(self.files)
        bestLessons = []
        for i in range(len(self.files)):
            if self.files[i] in best:
                bestLessons.append(1)
            else:
                bestLessons.append(0)
        return bestLessons

    def changeNextLessonButton(self):
        if self.doneWithAllLessons:
            self.ids.nextLessonButton.text = 'Redo Yellow Lesson'
        else:
            pass

    def changeLessonName(self):
        self.ids.lessonName.text = 'Lesson '+str(self.lessonNumber+1)
        
