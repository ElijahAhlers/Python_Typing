from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.gridlayout import GridLayout

import os
import datetime
from csv_object import csv_object

import Games.Modules.NoBackspaceEntry

import Games.Letter_Game.Letter_Game
import Games.Zerg_Rush.Zerg_Rush


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


class GamesMenuScreen(Screen):

    name = 'Games Menu'
    all_results = [{'name': 'Name', 'date': 'Date', 'score': 'Score', 'time': 'Time'}]
    best_results = [{'name': 'Name', 'date': 'Date', 'score': 'Score', 'time': 'Time'}]

    def populate(self):
        self.load_results()

    def load_results(self):
        with csv_object(
                f'{self.manager.manager.save_location}/User_History/{self.manager.manager.user.username}/GamesHistory.csv'
        ) as file:
            data = file.body

        self.ids.all_results.data = [
                     {'name': 'Name', 'date': 'Date', 'score': 'Score', 'time': 'Time'}
                 ] + sorted(
            data, key=lambda x: (x['date'].split('-')[2], x['date'], x['time_of_day']), reverse=True)

        self.ids.best_results.data = [
                      {'name': 'Name', 'date': 'Date', 'score': 'Score', 'time': 'Time'}
                  ] + sorted(best_scores(data), key=lambda x: x['name'])
    
    def exit(self):
        self.manager.manager.current = 'Part Select'
        Window.fullscreen = False


class GameLayout(GridLayout):

    def pressed(self, button):
        self.manager.current = button


class GamesMenuManager(ScreenManager):

    transition = NoTransition()
    manager = None
    allow_backspace = None
    words = None

    def populate(self):
        self.manager = self.parent.manager
        for screen in ['Games Menu']:
            self.get_screen(screen).populate()
        self.allow_backspace = True if open(
            f'{self.manager.save_location}/allow_backspace_in_games.txt').read() == 'True' else False
        self.words = open(
            f'{self.manager.save_location}/TypingFiles/GameWords/default_words.txt').read().split(' ')

    def leave_me(self):
        self.get_screen('Games Menu').load_results()
        self.current = 'Games Menu'

    def record_results(self, game_name, score, time):
        path = f'{self.manager.save_location}/User_History/{self.manager.user.username}/GamesHistory.csv'
        new_dic = {
            'name': game_name,
            'date': datetime.date.today().strftime("%m-%d-%y"),
            'score': str(int(score)),
            'time': str(int(time)),
            'time_of_day': int((datetime.datetime.now() - datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0)).total_seconds())
        }
        with csv_object(path) as file:
            file.header = ['name', 'date', 'score', 'time', 'time_of_day']
            file.body += [new_dic]


class GamesMenuManagerScreen(Screen):

    def populate(self):
        self.children[0].populate()
