# Built into python
import traceback

import logging

# Do stuff for log files
#if not os.path.isdir(str(open('Save Location.txt','r').read())+'Logs/'+str(date.today().strftime("%m-%d-%Y"))):
#    os.mkdir(str(open('Save Location.txt','r').read())+'Logs/'+str(date.today().strftime("%m-%d-%Y")))

#logName = str(str(open('Save Location.txt','r').read())+'Logs\\'+str(date.today().strftime("%m-%d-%Y"))+'\\TypingConsole___'+str(os.getlogin())+'___'+datetime.now().strftime("%d-%m-%Y___%H_%M_%S")+'.log')
#logging.basicConfig(filename=logName)


# Get rid of kivy info text
# os.environ["KIVY_NO_CONSOLELOG"] = '1'

# Checks for update, then updates program if needed
#if open('Save Location.txt').read()[-1] is not 's':
#    if str(open(open('Save Location.txt').read()+'/Version.txt').read()) != str(open('Version.txt').read()):
#        partial(os.system,'"Update Program.py"')()
#        exit('Finished Updating')

# Kivy stuff
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.core.window import Window
from kivy.config import Config

# Stuff we made
from GUI.LoginWindowgui import LoginWindow as LW
from GUI.ChangePasswordgui import firstLogin as CP
from GUI.LessonSelectgui import HomeWindow as LS
from GUI.TypingWindowgui import TypingWindow as TW
from GUI.ResultsScreenGUI import ResultsWindow as RW
from Games.GamesMenu import gameManager as GM
from GUI.TypingHistory import TypingHistory as TH

# Stuff we made
from Logic.UserClass import User as UserObject

# Set up kivy window
Window.borderless = True
Config.read('KivyGraphicFiles/config.ini')


# Main manager:  controls the different screens
# also holds information that needs to be shared with other programs/classes
class Manager(ScreenManager):

    day = None
    nextLesson = None

    # the user that logged in (default for debugging)
    user = UserObject('debugme')

    # Results being transferred to the results screen
    results = []
    idleTime = 0
    doneWithLessons = False
    resultsObject = None
    lesson = None

    location = open('Save Location.txt').read()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = NoTransition()

        self.add_widget(LW())
        self.add_widget(LS(self.user))
        self.add_widget(CP(self.user))
        self.add_widget(TH(self.user))
        self.add_widget(TW())
        self.add_widget(RW())

        screen = Screen(name='Games Menu')
        GM.user = self.user
        GM.screen.load_results()
        screen.add_widget(GM)
        self.add_widget(screen)

    def cheatyFunc(self):
        #Window.fullscreen = 'auto'
        self.current = 'LessonSelectScreen'


# Makes an app object to put the manager object on
class LoginMaster(App):
    def open_settings(self, *largs):
        pass

    def build(self):
        return Manager()

app = LoginMaster()


# Tries to run the app and if anything goes wrong, it logs it, then exits
try:
    app.run()
except Exception as error:
    logging.info(traceback.format_exc())
    print(error)
    input()
