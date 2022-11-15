from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

import os

from Games.LetterGame.LetterGame import LetterGameScreen as LGS

gamesScreenFormat = """
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        Label:
            size_hint_y: 0.1
            font_size: '30sp'
            text: 'Typing Games'
        GridLayout:
            padding: [root.width*0.02,root.height*0.02,root.width*0.02,root.height*0.02]
            size_hint_y: 0.8
            cols: 2"""
for game in os.listdir(os.getcwd()+'/Games'):
    gamesScreenFormat+="""
            GridLayout:
                cols:2
                Button:
                    text: '"""+game+"""'
                    on_press: root.parent.parent.goTo"""+game+"""()
                Label:
                    font_size: '20sp'
                    text_size: self.size
                    text: '"""+str(open(os.getcwd()+'\\Games\\'+game+'\\description.txt',mode = 'r').read())+"""'
                    valign: 'middle'"""
    
for i in range(10-(len(os.listdir(os.getcwd()+'/Games')))):
    gamesScreenFormat+="""
            Label:
                text: ''"""
            
    
    
gamesScreenFormat+="""
    
        Button:
            size_hint_y: 0.1
            text: 'Exit'
            on_press: root.exit()
"""

#print(gamesScreenFormat)
Builder.load_string(gamesScreenFormat)

class MenuScreen(Screen):
    def exit(self):
        self.parent.parent.parent.parent.current = 'LessonSelectScreen'

class GamesMaster(ScreenManager):

    def __init__(self,user,**kwargs):
        super().__init__(**kwargs)
        self.transition = NoTransition()
        self.addSelectScreen()
        self.user = user
        

    def addSelectScreen(self):
        self.GamesSelect = Screen(name = 'select')
        self.GamesSelect.add_widget(MenuScreen())
        self.add_widget(self.GamesSelect)

    def goToLetterGame(self):
        print(self.screens)
        if 'LetterGame' in [x.name for x in self.screens]:
            self.screens.pop([x.name for x in self.screens].index('LetterGame'))
            print('removed old one')
        self.add_widget(LGS(self.user))
        Window.fullscreen = 'auto'
        self.current = 'LetterGame'
        print(self.screens)

    def addGamesFromFolder(self):
        pass



    
        


    
