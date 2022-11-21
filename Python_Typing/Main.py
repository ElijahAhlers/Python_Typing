# Get rid of kivy info text
# os.environ["KIVY_NO_CONSOLELOG"] = '1'

# Kivy stuff
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
import os

# Stuff we made
from GUI.Login import LoginScreen
from GUI.Lesson_Select import LessonSelectScreen
from GUI.Change_Password import ChangePasswordScreen
from GUI.History import HistoryScreen
from GUI.Typing import TypingScreen
from GUI.Results import ResultsScreen
from Games.Games_Menu import GamesMenuScreen

# Set up kivy window
Window.borderless = True
Window.clearcolor = (0, 0, 0, 0)
Config.read('GUI/config.ini')
kv_files = [
    'Main.kv',
    'Login.kv',
    'Lesson_Select.kv',
    'Change_Password.kv',
    'History.kv',
    'Typing.kv',
    'Results.kv',
]
for kv_file in kv_files:
    Builder.load_file(f'GUI/{kv_file}')
Builder.load_file(f'Games/Games_Menu.kv')


class Manager(ScreenManager):

    lesson = None
    next_lesson = None
    user = None
    results_object = None
    save_location = os.getcwd()[:-len('Python_Typing')]+'Data'

    def populate(self):
        for screen in ['Lesson Select', 'Typing', 'Results', 'History', 'Change Password', 'Games Menu Manager']:
            self.get_screen(screen).populate()


class RootApp(App):
    def open_settings(self, *args):
        pass

    def build(self):
        manager = Manager()
        manager.transition = NoTransition()
        manager.get_screen('Login').populate()
        return manager


RootApp().run()
