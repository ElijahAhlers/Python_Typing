from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

import os
import datetime
import Logic.CSVFuncs as CSVFuncs

Builder.load_file('Games/GamesMenu.kv')


def best_scores(scores):

    different_games = []
    scores.sort(key=lambda x: x['name'])
    different_games += [scores[0]['name']]
    for score in scores:
        if score['name'] != different_games[-1]:
            different_games += [score['name']]

    best_games = []
    for name in different_games:
        best_games += [sorted([x for x in scores if x['name'] == name], key=lambda x: int(x['score']), reverse=True)[0]]

    return best_games


class MenuScreen(Screen):

    gameGrid = ObjectProperty(None)
    all_results = [{'name': 'Name', 'date': 'Date', 'score': 'Score', 'time': 'Time'}]
    best_results = [{'name': 'Name', 'date': 'Date', 'score': 'Score', 'time': 'Time'}]

    def load_results(self):
        if os.path.exists(open('Save Location.txt').read(
                )+'UserData/'+self.the_manager.user.username+'/GamesHistory.csv'):

            data = CSVFuncs.readCSVFile(open('Save Location.txt').read(
                    )+'UserData/'+self.the_manager.user.username+'/GamesHistory.csv')

            self.ids.all_results.data = [
                         {'name': 'Name', 'date': 'Date', 'score': 'Score', 'time': 'Time'}
                     ] + sorted(data, key=lambda x: (x['date'],x['time_of_day']), reverse=True)

            self.ids.best_results.data = [
                          {'name': 'Name', 'date': 'Date', 'score': 'Score', 'time': 'Time'}
                      ] + sorted(best_scores(data), key=lambda x: x['name'])
    
    def exit(self):
        self.get_root_window().children[0].current = 'LessonSelectScreen'
        Window.fullscreen = False


class GameLayout(GridLayout):

    button = ObjectProperty(None)
    description = ObjectProperty(None)
    
    def __init__(self, game_name, **kwargs):
        super().__init__(**kwargs)
        self.gameName = game_name

        self.button.text = self.gameName
        self.description.text = open('Games/'+self.gameName+'/description.txt').read()

    def pressed(self, button):
        self.parent.parent.parent.parent.parent.current = button


class GamesMaster(ScreenManager):

    transition = NoTransition()
    user = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.screen = MenuScreen(name='Game Picker')
        self.screen.the_manager = self
        self.add_widget(self.screen)
        self.allow_backspace = True if open(
            open('Save Location.txt').read()+'allow_backspace.txt').read()=='True' else False
        self.words = open(
            open('Save Location.txt').read()+'TypingFiles/GameWords/default_words.txt').read().split(' ')

    def make_game_buttons(self):
        for game, layout in gameScreensAndButtons:
            if game is not None:
                self.add_widget(game)
            self.screen.ids.GameGrid.add_widget(layout)

    def leave_me(self):
        self.screen.load_results()
        self.current = 'Game Picker'

    def record_results(self, game_name, score, time):
        path = open('Save Location.txt').read()+'UserData/'+self.user.username+'/GamesHistory.csv'
        new_dic = {
            'name': game_name,
            'date': datetime.date.today().strftime("%m-%d-%y"),
            'score': str(int(score)),
            'time': str(int(time)),
            'time_of_day': int((datetime.datetime.now() - datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        }
        if os.path.exists(path):
            CSVFuncs.writeToCSVFile(path, [new_dic])
        else:
            CSVFuncs.writeNewCSVFile(path, ['name', 'date', 'score', 'time', 'time_of_day'], [new_dic])


gameManager = GamesMaster()

gameScreensAndButtons = []

for gameName in [file for file in os.listdir('Games')
            if 'GamesMenu' not in file and 'Instructions' not in file and '__' not in file and 'Modules' not in file]:
    newGame = Screen(name=gameName)
    exec('from Games.{0}.{0} import {0}_Layout as Game'.format(gameName))
    newGame.add_widget(Game(gameManager))
    newLayout = GameLayout(gameName)
    gameScreensAndButtons += [[newGame, newLayout]]

for i in range(9-len(gameScreensAndButtons)):
    gameScreensAndButtons += [[None, Label()]]

gameManager.make_game_buttons()


if __name__ == '__main__':
        
    class MyApp(App):
        def build(self):
            return gameManager

    a = MyApp()
    a.run()
