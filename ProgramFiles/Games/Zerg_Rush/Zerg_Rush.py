from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from Games.Modules.NoBackspaceEntry import NoBackspaceEntry
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from random import random, randint, choice

person = ' o \n\\|/\n | \n/ \\'


def randomBorderCoord():
    '''Makes a random coordinate on the border
        of the screen. screen coords are (0,0) to (1,1)'''

    #Decide if it should choose bottom/top or left/right
    if randint(0, 1):

        #Bottom or top
        #0 or 1 # 0 thru 1
        return random(), randint(0, 1)

    else:

        # Left or right
        #       0 thru 1   # 0 or 1
        return randint(0, 1), random()


Builder.load_file('Games/Zerg_Rush/Zerg_Rush.kv')


class Zerg_Rush_Layout(BoxLayout):
    diff1 = ObjectProperty(None)
    diff2 = ObjectProperty(None)
    diff3 = ObjectProperty(None)
    diff4 = ObjectProperty(None)
    diff5 = ObjectProperty(None)
    score = ObjectProperty(None)
    endButton = ObjectProperty(None)
    gameScreen = ObjectProperty(None)
    beginInstructions = ObjectProperty(None)
    startButton = ObjectProperty(None)
    userInput = ObjectProperty(None)

    #words = open('Games/Modules/allwords.txt', 'r').read().split(' ')  #S:\Typing\PythonTyping\
    
    currentDifficulty = 'Easy'
    started = False
    timeToCenter = 20

    difficultyLookUp = {
        'Easy': {
            'Frequency': 40,
            'Ramping': 1.005,
            'Multiplier': 2  # 1  (typed 1338 characters  score 2676 on 5/6  342 seconds)
        },
        'Medium': {
            'Frequency': 30,
            'Ramping': 1.0075,
            'Multiplier': 4  # 2  (typed 784 characters  score 3136 on 5/6  171 seconds)
        },
        'Hard': {
            'Frequency': 26,  # 30,
            'Ramping': 1.010,
            'Multiplier': 6  # 3  (typed 549 characters  score 3276 on 5/6  118 seconds)
        },
        'Very Hard': {
            'Frequency': 22,  # 20,
            'Ramping': 1.015,
            'Multiplier': 9  # 4  (typed 388 characters  score 3492 on 5/6  75 seconds)
        },
        'Good Luck': {
            'Frequency': 6,  # 2,
            'Ramping': 1,
            'Multiplier': 18  # (typed 202 characters  score 3636 on 5/6  34 seconds)
        },
    }

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)

        self.manager = manager
        self.words = manager.words
        self.userInput.disable_backspace = not self.manager.allow_backspace
        self.chgDif(self.currentDifficulty)

        self.allSpawns = []
        self.wordSpawns = []
        self.userInput.bind(text=self.checkSpacebar)

    def checkSpacebar(self, instence, value):
        self.userInput.focus = True
        if value and (value[-1] == ' ' or value[-1] == '\n'):
            if self.started:
                self.attemptWordRemoval(value[:-1])
            # else:
            #   self.start()
            self.userInput.text = ''

    def start(self):
        self.time_counter = 0
        self.userInput.text = ''
        self.userInput.focus = True
        self.sinceLastSpawn = 1
        self.spawnFrequency = self.difficultyLookUp[self.currentDifficulty]['Frequency']
        self.difficultyRamping = self.difficultyLookUp[self.currentDifficulty]['Ramping']
        self.scoreMultiplier = self.difficultyLookUp[self.currentDifficulty]['Multiplier']
        self.started = True
        self.score.text = '0'
        self.startButton.disabled = True
        self.endButton.text = 'Die Now'
        self.endButton.on_release = self.end
        self.beginInstructions.text = '·'
        self.changeButtonDisabledPropertyForDifficultyButtons(True)
        self.spawning = Clock.schedule_interval(self.update, .05)
        self.counting = Clock.schedule_interval(self.increment_timer, 1)

    def end(self):
        self.manager.record_results('Zerg Rush', self.score.text, self.time_counter)
        self.started = False
        self.startButton.disabled = False
        self.endButton.text = 'Exit'
        self.endButton.on_release = self.Exit
        self.beginInstructions.text = 'You Died'
        self.chgDif(self.currentDifficulty)
        Clock.unschedule(self.spawning)
        Clock.unschedule(self.counting)
        for label in self.allSpawns:
            label.parent.remove_widget(label)
        self.allSpawns = []
        self.wordSpawns = []

    def increment_timer(self, interval):
        self.time_counter += 1

    def update(self, dt):
        self.sinceLastSpawn += 1
        if self.sinceLastSpawn >= self.spawnFrequency:
            self.sinceLastSpawn = 0
            self.spawnFrequency = self.spawnFrequency / self.difficultyRamping
            self.spawnNew()

    def spawnNew(self):
        word = choice(self.words)
        x, y = randomBorderCoord()
        label = Label(text=word, size_hint=[.2, .2], pos_hint={'x': x - .1, 'y': y - .1})
        self.gameScreen.add_widget(label)
        movement = Animation(
            pos_hint={'x': .4, 'y': .4},
            duration=self.timeToCenter)
        movement.bind(on_complete=self.spawnReachedCenter)
        movement.start(label)
        self.allSpawns += [label]
        self.wordSpawns += [word]

    def spawnReachedCenter(self, animation, label):
        if label in self.allSpawns:
            self.end()

    def attemptWordRemoval(self, word):
        if word in self.wordSpawns:
            self.ids.score.text = str(int(self.ids.score.text) + (len(word) * self.scoreMultiplier))
            index = self.wordSpawns.index(word)
            self.allSpawns[index].parent.remove_widget(self.allSpawns[index])
            self.allSpawns.pop(index)
            self.wordSpawns.pop(index)

    def chgDif(self, newDifficulty):
        self.changeButtonDisabledPropertyForDifficultyButtons(False)
        numericDiff = list(self.difficultyLookUp.keys()).index(newDifficulty) + 1
        exec('self.diff{0}.disabled = True'.format(
            str(numericDiff)))
        self.currentDifficulty = newDifficulty

    def changeButtonDisabledPropertyForDifficultyButtons(self, abool):
        self.diff1.disabled = abool
        self.diff2.disabled = abool
        self.diff3.disabled = abool
        self.diff4.disabled = abool
        self.diff5.disabled = abool

    def Exit(self):
        if not self.started:
            self.manager.leave_me()


if __name__ == '__main__':
    class Root(App):
        def build(self):
            return Zerg_Rush_Layout()


    root = Root()
    root.run()
