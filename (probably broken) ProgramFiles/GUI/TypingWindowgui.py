#Python Standard Library
import threading as thread
import time as perf
from datetime import date
from time import sleep
import time
import logging
from os.path import exists as fileExists
import os


#Pynput stuff
from pynput import keyboard
from pynput.keyboard import Key as keyModule

#Kivy stuff
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

#Stuff we made
from Logic.CSVFuncs import *

class TypingWindow(GridLayout):

#Define constant variables for this class and all it's instances

    #load kivy foramtting
    Builder.load_file('KivyGraphicFiles/TypingWindow.kv')

    #variables for keylogger
    listOfLetters = 'abcdefghijklmnopqrstuvwxyz'
    listOfNumbersAndSymbols = "1234567890-=,./;'`[]\\"
    listOfCorrespondingSymbols = '!@#$%^&*()_+<>?:"~{}|'

    #Options for typing window
    
    #           wrong     correct    
    colors = ['#ff0069','#00ffff']

    cursor = '_'
    secondsOfIdleTimeAllowed = 5
    numOfLettersShownOnTheScreen = 74
    percentOfSpaceLeftAfterYourTyping = .5

    #define other measurements based on your choices above
    lettersOnScreen = int(numOfLettersShownOnTheScreen*(1-percentOfSpaceLeftAfterYourTyping))
    spacesOnScreen = numOfLettersShownOnTheScreen-lettersOnScreen
 
###################################################################################################################################

#Define the initiation of the window.
    
    def __init__(self, day, lesson, user,**kwargs):
        '''Will make a running lesson instance.
        Parameters: day object, lesson object, user object
        Returns: class instance of RunningLesson'''

        #makes itself a grid layout
        super().__init__(**kwargs)

        #saves passed variables for later use
        self.day = day
        self.lesson = lesson
        self.totalTimeInLesson = lesson.time
        self.wordsToType = [chr for chr in lesson.text]+[' ']
        self.bSpace = lesson.backspace
        self.forced100 = lesson.forced100
        self.totalTime = lesson.time
        self.time = lesson.time
        self.filename = lesson.filename
        self.user = user

        #sets up time counters
        self.idleTimeCache = perf.perf_counter()
        self.timeCache = perf.perf_counter()

        #more window configuration
        Window.fullscreen = 'auto'

        #define variables that the lesson needs to start
        self.onScreenText = []
        self.typedText = []
        self.lettersRight = []
        self.currentCursor = self.cursor #this is a dumb line that is a failed attempt at a blinky cursor that i am too lazy to take out
        self.fileIdleTime = 0
        self.accuracy = 100
        self.rawWPM = 0
        self.realWPM = 0
        self.lettersTyped = 0
        self.runclock = True
        self.returnKeyPresses = False
        self.shiftDownl = False
        self.shiftDownr = False
        self.ctrlDownl = False
        self.ctrlDownr = False
        self.capsToggle = False

        #starts the lesson
        self.makeWindow()
        
###################################################################################################################################
###################################################################################################################################
#Window layout stuff
     
    def changevar(self,var,attr,value):
        '''Changes your variable's attribute to your value
        Parameters: str, str, any
        Returns: None'''
        exec('self.ids.'+str(var)+'.'+str(attr)+' = "'+str(value)+'"')
        
    def exit(self):
        """Records results and then goes to the results screen.
        Parameters: None
        Returns: None"""
        self.recordResults()
        #adds results to screen manager object
        self.parent.parent.results.append([self.filename,str(self.accuracy),str(self.realWPM)])
        self.parent.parent.idleTime+=self.fileIdleTime
        #makes the results window
        self.parent.parent.GoToResults()
        #switches to the results window
        self.parent.parent.current = 'ResultsWindow'


    def prepScreen(self):
        """adds unchanging values to the screen, stuff not affected by redo
        Parameters: None
        Returns: None"""
        self.ids.firstname.text = self.user.firstName
        self.ids.lastname.text = self.user.lastName
        self.ids.lessonNum.text = 'Lesson '+str(self.lesson.part+1)+' of '+str(len(self.day.files))
        self.ids.filename.text = self.filename
        self.ids.givenText.text = self.makeLetterDisplayString()
        self.ids.typedText.text = ''
        self.ids.accuracy.text = '0'
        self.ids.rawwpm.text = '0'
        self.ids.realwpm.text = '0'
        self.ids.time.text = self.formatTime(self.time)
        self.ids.idletime.text = '00:00'
        self.ids.percentcomplete.text = self.addZeroesToPercent(0)
        self.ids.bsonoff.text = 'Backspace is ' + ('on' if self.bSpace else 'off')
        self.ids.forced100.text = 'Forced Accuracy is ' + ('on' if self.forced100 else 'off')


        
###################################################################################################################################
###################################################################################################################################
#Logic stuff
###################################################################################################################################

#Define the running of the window.  Will make the window.
        
    def makeWindow(self):
        """Gets the screen ready and then starts it.
        Parameters: None
        Returns: None"""
        self.prepScreen()
        self.startClock()
        self.StartKeyLogger()
        self.returnKeyPresses = True
        #Window.fullscreen = 'auto'

#####################################################################################################################
        
    def redo(self):
        """Redefines variables to start over, then starts over.
        Parameters: None
        Returns: None"""
        self.stopClock()
        self.StopKeyLogger()
        self.lettersRight = []
        self.totalTime = self.totalTimeInLesson
        self.time = self.totalTimeInLesson
        self.onScreenText = []
        self.typedText = []
        self.percentComplete = 0
        self.ids.givenText.text = ''
        self.ids.typedText.text = ''
        self.ids.accuracy.text = '0'
        self.ids.rawwpm.text = '0'
        self.ids.realwpm.text = '0'
        self.ids.time.text = self.formatTime(self.time)
        self.ids.percentcomplete.text = self.addZeroesToPercent(0)
        self.ids.percentprogress.value = 0
        self.lettersTyped = 0
        self.prepScreen()
        self.clockThread.join()
        self.timeCache = perf.perf_counter()
        self.startClock()
        self.StartKeyLogger()

#####################################################################################################################

#Define functions for keylogger
        
    def StartKeyLogger(self):
        self.listener = keyboard.Listener(on_press=self.KeyPress, on_release=self.KeyRelease)
        self.listener.start()

    def StopKeyLogger(self):
        self.listener.stop()

    def KeyPress(self, key):
        if self.returnKeyPresses:
            self.IdentifyKey(key,False)
            self.idleTimeCache = perf.perf_counter()

    def KeyRelease(self, key):
        if key == keyModule.shift:
            self.shiftDownl = False
        elif key == keyModule.shift_r:
            self.shiftDownr = False
        elif key == keyModule.ctrl_l:
            self.ctrlDownl = False
        elif key == keyModule.ctrl_r:
            self.ctrlDownr = False

    def IdentifyKey(self, key, down):
        try:
            if self.ctrlDownl or self.ctrlDownr:
                pass  #Eat all keys when ctrl is pressed
            elif key.char in self.listOfLetters:
                self.KeyPressMaster(key.char if (not self.shiftDownl) and (not self.shiftDownr) and (not self.capsToggle) else key.char.upper())
            elif key.char in self.listOfNumbersAndSymbols:
                self.KeyPressMaster(key.char if (not self.shiftDownl) and (not self.shiftDownr) else self.listOfCorrespondingSymbols[self.listOfNumbersAndSymbols.index(key.char)])
            else:
                self.KeyPressMaster(key.char if (not self.capsToggle) or self.shiftDownl or self.shiftDownr else key.char.lower())
            
        except AttributeError:
            if key == keyModule.space:
                self.KeyPressMaster(' ')
            elif key == keyModule.caps_lock:
                self.capsToggle = not self.capsToggle
            elif key == keyModule.shift:
                self.shiftDownl = True
            elif key == keyModule.shift_r:
                self.shiftDownr = True
            elif key == keyModule.ctrl_l:
                self.ctrlDownl = True
            elif key == keyModule.ctrl_r:
                self.ctrlDownr = True
            elif key == keyModule.backspace:
                self.KeyPressMaster('bspace') if self.bSpace else None
            else:
                logging.info(key)
        
        except TypeError:
        
            #Eat the key press if it is a numpad keypress
            pass

    def makeKeyString(self):
        if len(self.onScreenText) > self.lettersOnScreen:
            return ''.join(self.onScreenText)+self.currentCursor+' '*(self.spacesOnScreen-1)
        else:
            return ''.join(self.onScreenText)+self.currentCursor+' '*(self.numOfLettersShownOnTheScreen-len(self.onScreenText)-1)

    def makeLetterDisplayString(self):
        if self.lettersTyped > self.lettersOnScreen:
            screentext = self.wordsToType[self.lettersTyped-self.lettersOnScreen:self.lettersTyped-self.lettersOnScreen+self.numOfLettersShownOnTheScreen]
            return ''.join(screentext) + ' '*(self.numOfLettersShownOnTheScreen-len(''.join(screentext)))
        else:
            return ''.join(self.wordsToType[:self.numOfLettersShownOnTheScreen])+' '*(self.numOfLettersShownOnTheScreen-len(self.wordsToType[:self.numOfLettersShownOnTheScreen]))
            
    def KeyPressMaster(self,key):
        self.tryToMakeTheRedoButton()
        self.idleTimeCache = perf.perf_counter()
        if key == 'bspace':
            self.subtractLetter()
            
        elif self.forced100:
            if key == self.wordsToType[self.lettersTyped]:
                self.addLetter(key,True)
                   
        else:
            self.addLetter(key, self.wordsToType[self.lettersTyped] == key)
        
        self.ids.typedText.text = self.makeKeyString()
        self.ids.givenText.text = self.makeLetterDisplayString()
        self.calculatePercent()
        self.ids.percentcomplete.text = self.addZeroesToPercent(self.percentComplete)
        self.ids.percentprogress.value = int(self.percentComplete)
        if self.lettersTyped == len(self.wordsToType):
            self.Exit()

    def addLetter(self,letter,right):
        """Takes a letter and if it is right, and formats it for kivy
        Adds the letter to the lists of letters needed to display on the screen
        Parameters: str, bool
        Returns: None"""
        
        color = self.colors[int(right)]
        self.lettersRight.append(right)
        
        if letter == ' ':
            formattedLetter=[' ']
##        elif letter == '|':
##            formattedLetter=['|']
        elif letter == '"':
            formattedLetter=['[color='+color+']\"[/color]']
        elif letter == '[':
            formattedLetter=['[color='+color+']&br;[/color]']
        elif letter == ']':
            formattedLetter=['[color='+color+']&bl;[/color]']
        else:
            formattedLetter=['[color='+color+']'+letter+'[/color]']
            
        self.typedText += formattedLetter
        self.onScreenText += formattedLetter
        self.lettersTyped+=1
        if self.lettersTyped > self.lettersOnScreen:
            self.onScreenText = self.onScreenText[1:]

            
    def subtractLetter(self):
        if not self.lettersTyped:
            return None
        elif self.lettersTyped <= self.lettersOnScreen:
            self.lettersRight = self.lettersRight[:-1]
            self.lettersTyped-=1
            self.onScreenText = self.onScreenText[:-1]
            self.typedText = self.typedText[:-1]
        else:
            self.lettersRight = self.lettersRight[:-1]
            self.lettersTyped-=1
            self.onScreenText = self.onScreenText[:-1]
            self.onScreenText = [self.typedText[self.lettersTyped-self.lettersOnScreen]]+self.onScreenText
            self.typedText = self.typedText[:-1]

        
###################################################################################################################################

#Define functions to use in the program later

    def formatTime(self, sec):
        '''Formats a time in seconds to mm:ss
        Parameters: int
        Returns: str'''
        minutes,seconds = str(sec//60),str(sec%60)
        minutes = '0'*(2-len(minutes))+minutes
        seconds = '0'*(2-len(seconds))+seconds
        return minutes+':'+seconds
       
    def formatDaClock(self,time):
        """Formats time into hours:minutes:seconds
        Parameters: time object
        Returns: str"""
        return '''{0}:{1}:{2}'''.format(self.possiblyAddAZero(time.tm_hour),
                                        self.possiblyAddAZero(time.tm_min),
                                        self.possiblyAddAZero(time.tm_sec))
    
    def possiblyAddAZero(self, integer):
        """If a one digit integer is inputted, add a 0 else nothing
        Parameters: int
        Returns: str"""
        return str(integer) if str(integer)[:-1] else '0'+str(integer)

    def addZeroesToPercent(self, percent):
        """Takes an integer and formats it to look decent
        Parameters: int
        Returns: str"""
        return 'Percent Complete: '+' '*(3-len(str(percent)))+str(percent)+'%'

    def calculateRealWPM(self):
        self.realWPM = int(((self.lettersRight.count(True)/5)-self.lettersRight.count(False))/(self.totalTime-self.time)*60)

    def calculateAccuracy(self):
        self.accuracy = round(self.lettersRight.count(True)/self.lettersTyped*100,1) if self.lettersTyped else 0

    def calculateRawWPM(self):
        self.rawWPM = int((self.lettersTyped/5)/(self.totalTime-self.time)*60)

    def calculatePercent(self):
        self.percentComplete = int(self.lettersTyped/len(self.wordsToType)*100)
    
    def tryToMakeTheRedoButton(self):
        self.children[3].children[1].children[6].children[0].makaDaButton()

###################################################################################################################################

#Define functions for the clock loop

    def startClock(self):
        self.runclock = True
        self.clockThread = thread.Thread(target=self.clockLoop)
        self.clockThread.start()

    def clockLoop(self):
        def checkIfDone():
            if not self.runclock:
                raise ThreadTerminator('I was told to die')
        while self.runclock:
            try:
                timeToWait = (self.timeCache+1-perf.perf_counter())/4
                for i in range(4):
                    sleep(timeToWait)
                    checkIfDone()
                self.timeCache = perf.perf_counter()
                self.clockUpdate()
                if self.timeCache-self.idleTimeCache > self.secondsOfIdleTimeAllowed:
                    self.fileIdleTime+=1
                    self.ids.idletime.color = 1,0,0,1
                if not self.time:
                    self.runclock = False
                    self.Exit()
            except ThreadTerminator:
                break

    def stopClock(self):
        self.runclock = False

    def clockUpdate(self):
        self.time -= 1
        self.calculateAccuracy()
        self.calculateRealWPM()
        self.calculateRawWPM()
        if self.accuracy >= 80:
            self.ids.accuracy.color = 0,1,1,1
        elif self.accuracy >= 50:
            self.ids.accuracy.color = 1,.5,.5,1
        else:
            self.ids.accuracy.color = 1,0,0,1
        self.ids.clockThingThatTheyWant.text = self.formatDaClock(time.localtime())
        self.ids.accuracy.text = str(self.accuracy)
        self.ids.rawwpm.text = str(self.rawWPM)
        self.ids.realwpm.text = str(self.realWPM)
        self.ids.time.text = self.formatTime(self.time)
        self.ids.idletime.text = self.formatTime(self.fileIdleTime)
        #Blinking cursor thing that didn't work self.currentCursor = ' ' if self.currentCursor == self.cursor else self.cursor

###################################################################################################################################

#Define how to record results

    def recordResults(self):
        fileAlreadyMade = True
        file = self.parent.parent.location+'/UserData/'+self.user.username+'/History'

        if not fileExists(file):
            os.mkdir(file)

        file += '/'+str(date.today())+self.day.lessonName+'.csv'
        
        if fileExists(file):            
            writeToCSVFile(file,[{'Lesson':self.lesson.filename,
                                'Accuracy':self.accuracy,
                                'WPM':self.realWPM,
                                'Idle Time': self.fileIdleTime}])
        else:
            writeNewCSVFile(file,['Lesson','Accuracy','WPM','Idle Time'],
                           [{'Lesson':self.lesson.filename,
                            'Accuracy':self.accuracy,
                            'WPM':self.realWPM,
                            'Idle Time': self.fileIdleTime}])

        self.parent.parent.resultsObject.addResults(
            lessonName = self.lesson.filename,
            accuracy = self.accuracy,
            wpm = self.realWPM,
            idleTimeInLesson = self.fileIdleTime
            )
        self.parent.parent.resultsObject.totalIdleTime+=self.fileIdleTime
        
###################################################################################################################################

#Define exit function

    def Exit(self):
        self.calculateAccuracy()
        self.calculatePercent()
        self.calculateRealWPM()
        self.StopKeyLogger()
        self.stopClock()
        self.exit()

        
###################################################################################################################################

class MyRedoButton(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.doneMakingButton = False
    
    def makaDaButton(self):
        if not self.doneMakingButton:
            logging.info('The manager\'s "done with lessons" tag returned '+str(self.parent.parent.parent.parent.parent.parent.doneWithLessons))
        if not self.doneMakingButton and (self.parent.parent.parent.parent.parent.parent.doneWithLessons or self.parent.parent.parent.parent.bSpace):
            self.add_widget(Button(text='Redo', on_press=self.redo))
        self.doneMakingButton = True

    def redo(self,var):
        self.parent.parent.parent.parent.redo()

class ThreadTerminator(Exception):
    pass
