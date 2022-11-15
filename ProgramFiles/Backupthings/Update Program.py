from random import random,randint
import shutil
import sys
import os
from threading import Thread
from time import sleep

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.lang import Builder


builderfile = '''


<UpdateScreen>:

    cols: 1

    GridLayout:

        cols: 1
        padding: [.1,.1,.1,.1]
        
        Label:

            text: "Wait for the progress bar, then close and restart the program. \\nUpdating...."

    GridLayout:

        cols: 1
        padding: [69,69,69,69]
        
        ProgressBar:

            id: percentprogress
            max: 100
            value: 0

    GridLayout:

        cols: 3
        padding: [.1,.1,.1,.1]

'''+'''

        Label:
            text: ''

'''*4+'''
        
        Button:

            text: 'Close'
            on_press: root.Exit()



'''+'''

        Label:
            text: ''

'''*2

class UpdateScreen(GridLayout):

    
    Builder.load_string(builderfile)

    pbvalue = 0
    canFinish = False

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
##        Clock.schedule_once(self.startClock, randint(1,5))
##        Clock.schedule_once(self.accuallyUpdateTheProgram, 2)
        self.startClock(0)
        self.updateTheProgram(0)

    def Exit(self):
        print(self.get_root_window().children[0])
        if self.ids.percentprogress.value > 97:
            self.get_root_window().close()

    def startClock(self,dummyvar):
        Thread(target=self.barTick).start()

    def updateTheProgram(self,dummyvar):
        Thread(target=self.accuallyUpdateTheProgram).start()

    def accuallyUpdateTheProgram(self):
        location = open('Save Location.txt').read()
        for item in os.listdir():
            if '.' not in item[1:]:
                shutil.rmtree(item)
            elif item == 'Update Program.py':
                pass
            else:
                os.remove(item)
        for item in os.listdir(location+'ProgramFiles'):
            print(item)
            print(sys.path[0])
            currentDir = location+'ProgramFiles/'+item
            print(currentDir)
            print()
            try:
                shutil.copytree(currentDir,sys.path[0]+'/'+item)
            except:
                shutil.copyfile(currentDir,sys.path[0]+'/'+item)
        self.canFinish = True

    def barTick(self):
        while self.pbvalue<100:
            randomtick = randint(1,8)
            self.pbvalue += randomtick if self.pbvalue+randomtick < 97 else (97-self.pbvalue if not self.canFinish else 100-self.pbvalue)
            self.ids.percentprogress.value = self.pbvalue
            sleeptime = random()
            print(sleeptime)
            sleep(sleeptime)



class UpdateApp(App):

    def build(self):
        
        return UpdateScreen()

app = UpdateApp()
app.run()


        
