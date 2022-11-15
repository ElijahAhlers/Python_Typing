from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.label import Label
import time as perf
import random
import threading

Builder.load_file('Games/Letter_Game/Letter_Game.kv')

# from Logic.CSVFuncs import *
letter_look_up = [['a', 's', 'd', 'f', 'j', 'k', 'l', ';'],
                  ['e', 'h', 'o', 'r'],
                  ['i', 't', 'u', 'c'],
                  ['n', 'w', 'g', 'p'],
                  ['m', 'x', 'y', 'z','q'],
                  ['.', ',', ':', '?'],
                  ['"', "'", '-'],
                  [],
                  ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                  ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '<', '>']]
symbols = ".,;/'-1234567890"
corresp = '><:?"_!@#$%^&*()'


def format_time(sec):
    minutes, seconds = str(int(sec // 60)), str(int(sec % 60))
    minutes, seconds = minutes if len(minutes) > 1 else '0' + minutes, seconds if len(
        seconds) > 1 else '0' + seconds
    minutes, seconds = minutes if len(minutes) > 1 else '00', seconds if len(seconds) > 1 else '00'
    return minutes + ':' + seconds


class LetterGrid(GridLayout):

    cols = 10

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.gameStarted = False
        self.labels = []
        self.errors = 0
        self.letters = [' ']
        self.gridWidth = 10
        self.gridHeight = 10
        self.build_letter_grid()
        self.answers = []
        self.caps = False
        self.current_letter = None

    def letter_pressed(self, keyboard, ascii_tuple, letter, modifiers):
        if 'shift' in modifiers:
            letter = letter.upper() if letter not in symbols else corresp[symbols.index(letter)]
        if 'ctrl' in modifiers and 'alt' in modifiers and 'shift' in modifiers and letter == '`':
            threading.Thread(target=self.test_mode).start()
        if self.current_letter is not None and letter == self.current_letter.text:
            self.make_letters_disappear(self.current_letter)
            if self.answers:
                self.choose_letter_to_type()
            else:
                self.parent.parent.parent.parent.end_game()
        else:
            self.errors += 1

    def build_letter_grid(self):
        for i in range(100):
            new_widget = Label(text='')
            self.labels += [new_widget]
            self.add_widget(new_widget)

    def make_answers(self):
        self.answers = []
        for i in range(self.gridWidth * self.gridHeight):
            self.answers += [random.choice(self.letters+(
                [letter.upper() for letter in self.letters if letter not in symbols] if self.caps else []))]

    def fill_letters(self):
        for index, letter in enumerate(self.answers, start=0):
            self.labels[index].text = letter
            self.labels[index].font_size = '18sp'

    def choose_letter_to_type(self):
        chosen_letter = random.choice([label for label in self.labels if label.text != ''])

        chosen_letter.color = (.8, 0, .1, 1)
        chosen_letter.bold = True
        chosen_letter.font_size = '50sp'

        self.current_letter = chosen_letter

    def make_letters_disappear(self, letter):
        self.answers.remove(letter.text)
        letter.text = ''
        letter.color = (1, 1, 1, 1)
        letter.font_size = '18sp'

    def test_mode(self):
        while len(self.answers) > 1:
            perf.sleep(0.05)
            self.letter_pressed(None, None, self.current_letter.text, [])


class Letter_Game_Layout(BoxLayout):

    timeAllowed = ObjectProperty(None)
    letterGrid = ObjectProperty(None)
    winLoss = ObjectProperty(None)
    difficulty_slider = ObjectProperty(None)

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)

        self.time = int
        self.finished = False
        self.keyboard = None
        self.manager = manager
        self.clock = None
        self.game_status = 'Ready to Start'
        self.valueStarted = 180
        self.difficulty_slider.bind(value=self.change_time_selection)

    def change_time_selection(self, instance, value):
        self.ids.timeAllowed.text = format_time(value)

    def set_selector_buttons(self, boolean):
        self.ids.hr.disabled = boolean
        self.ids.ehor.disabled = boolean
        self.ids.ituc.disabled = boolean
        self.ids.nwgbp.disabled = boolean
        self.ids.mxyzq.disabled = boolean
        self.ids.perComColQuest.disabled = boolean
        self.ids.quoteApostHyp.disabled = boolean
        self.ids.Cap.disabled = boolean
        self.ids.Num.disabled = boolean
        self.ids.specChar.disabled = boolean

    def set_selector_buttons_states(self, attr):
        self.ids.hr.state = attr
        self.ids.ehor.state = attr
        self.ids.ituc.state = attr
        self.ids.nwgbp.state = attr
        self.ids.mxyzq.state = attr
        self.ids.perComColQuest.state = attr
        self.ids.quoteApostHyp.state = attr
        self.ids.Cap.state = attr
        self.ids.Num.state = attr
        self.ids.specChar.state = attr

    def update_time_left(self, clock):
        self.time -= 1
        self.ids.difficulty.value = self.time
        self.ids.timeAllowed.text = format_time(self.time)
        if self.time == 0:
            self.end_game()

    def end_game(self):
        Clock.unschedule(self.clock)
        self.keyboard.unbind(on_key_down=self.letterGrid.letter_pressed)
        self.keyboard.release()
        self.keyboard = None
        self.ids.winLoss.text = 'Game Over' if self.time == 0 else 'You Win!'
        self.exit_button.text = 'Exit'
        self.ids.BeginButton.text = 'Start New Game'
        self.game_status = 'Waiting for Setup'
        self.record_results()
        self.ids.BeginButton.disabled = False

    def begin_button_call(self):
        if self.game_status == 'Ready to Start':
            self.begin_game()
            self.game_status = 'Started'
        elif self.game_status == 'Waiting for Setup':
            self.setup_new_game()
            self.game_status = 'Ready to Start'

    def begin_game(self):
        self.keyboard = Window.request_keyboard(None,self,'string')
        self.keyboard.bind(on_key_down=self.letterGrid.letter_pressed)
        self.exit_button.text = 'End Game'
        self.valueStarted = self.ids.difficulty.value
        self.time = self.ids.difficulty.value
        self.ids.BeginButton.disabled = True
        self.ids.difficulty.disabled = True
        self.set_selector_buttons(True)
        self.clock = Clock.schedule_interval(self.update_time_left, 1)
        self.letterGrid.choose_letter_to_type()

    def setup_new_game(self):
        print('setup')
        self.letterGrid.errors = 0
        self.ids.difficulty.value = self.valueStarted
        self.ids.difficulty.disabled = False
        self.ids.BeginButton.text = 'Begin'
        self.reset_game_board()

    def record_results(self):
        time_used = self.valueStarted - int(self.time)
        time_used = 300 - time_used
        time_used = time_used * 10
        time_used = time_used - (self.valueStarted * 5)
        score = time_used - self.letterGrid.errors * 10
        for i in range(len(self.letterGrid.answers)):
            score = score // 1.02
        self.manager.record_results('Letter Game', int(score), self.valueStarted-int(self.time))


    def exit(self):
        if self.keyboard is not None:
            self.end_game()
        else:
            self.manager.leave_me()

    def change_letters(self, adding, num):
        if num != 7:    #If the button pressed is not caps
            letters = letter_look_up[int(num)]
            if not adding:
                self.letterGrid.letters = [i for i in
                                           self.letterGrid.letters if
                                           i not in letters]
                if len(self.letterGrid.letters) == 0:
                    self.letterGrid.letters.append(' ')
            else:
                if self.letterGrid.letters[0] == ' ':
                    self.letterGrid.letters.remove(' ')
                    self.letterGrid.letters += letters
                else:
                    self.letterGrid.letters += [letter for letter in letters]
        else:
            self.letterGrid.caps = not self.letterGrid.caps
        self.letterGrid.make_answers()
        self.letterGrid.fill_letters()

        selection_button_states = [x.state for x in self.ids.letter_selection_buttons.children]

        self.ids.BeginButton.disabled = not (selection_button_states[3:9].count('down') >= 2 or (
                selection_button_states[:2]+[selection_button_states[9]]).count('down'))
        self.ids.Cap.disabled = not selection_button_states[5:].count('down')


    def reset_game_board(self):
        self.set_selector_buttons(False)
        self.ids.Cap.disabled = True
        self.set_selector_buttons_states('normal')
        self.ids.BeginButton.text = 'Begin'
        self.ids.winLoss.text = ''
        self.letterGrid.errors = 0
        self.letterGrid.letters = [' ']
        self.letterGrid.make_answers()
        self.letterGrid.fill_letters()
        self.ids.BeginButton.disabled = False
