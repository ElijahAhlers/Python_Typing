# Python Standard Library
import time

# Kivy stuff
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock


def calculate_real_wpm(total_letters, correct_letters, elapsed_time):
    return int((correct_letters-(total_letters - correct_letters))/(elapsed_time*5)*60) if elapsed_time else 0


def calculate_accuracy(total_letters, correct_letters):
    return round((correct_letters / total_letters) * 100, 1) if total_letters else 0


def calculate_raw_wpm(correct_letters, elapsed_time):
    return int((correct_letters/5)/elapsed_time*60) if elapsed_time else 0


class TypingScreen(Screen):

    name = 'Typing'

    #           wrong     correct    
    colors = ['#ff0069', '#00ffff']

    secondsOfIdleTimeAllowed = 5
    total_char_width = 74
    percentOfSpaceLeftAfterYourTyping = .5

    # define other measurements based on your choices above
    max_char_on_screen = int(total_char_width*(1-percentOfSpaceLeftAfterYourTyping))
    spaces_on_screen = total_char_width - max_char_on_screen

    symbols = ".,;/'-1234567890"
    corresp = '><:?"_!@#$%^&*()'
    acceptable_characters = '.,;/\'-1234567890><:?"_!@#$%^&*()abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ '

    typed_letters = []
    on_screen_letters = []
    file_idle_time = 0
    accuracy = 100
    rawWPM = 0
    realWPM = 0
    lesson_clock = None
    seconds_without_key_presses = 0
    on_key_press = 0
    total_time = None
    time_left = None
    lesson_letters = None
    keyboard = None
    lesson = None

    def populate(self):
        self.ids.firstname.text = self.manager.user.first_name
        self.ids.lastname.text = self.manager.user.last_name

    def start_lesson(self):
        Window.fullscreen = 'auto'
        self.lesson = self.manager.lesson.lesson_list[self.manager.next_lesson]
        self.ids.lessonNum.text = f'Part {self.manager.next_lesson + 1} of {len(self.manager.lesson.lesson_list)}'
        self.total_time = self.time_left = self.lesson.time
        self.lesson_letters = [character for character in self.lesson.text] + [' ']
        self.ids.filename.text = self.lesson.name

        # set up key presses
        if not self.keyboard:
            self.keyboard = Window.request_keyboard(None, self, 'string')
            self.keyboard.bind(on_key_down=self.pressed_letter)

        self.typed_letters = []
        self.on_screen_letters = []
        self.on_key_press = 0
        self.ids.typedText.text = ''
        self.ids.accuracy.text = '0'
        self.ids.rawwpm.text = '0'
        self.ids.realwpm.text = '0'
        self.ids.percentprogress.value = 0
        self.ids.redo.disabled = True
        self.ids.percentcomplete.text = 'Percent complete: {:0>3.0%}'.format(0)

        self.time_left = self.lesson.time
        self.ids.givenText.text = ''.join(self.lesson_letters[:self.total_char_width])
        self.ids.givenText.text += ' '*(self.total_char_width-len(self.ids.givenText.text))
        self.ids.time.text = '{:0>2}:{:0>2}'.format(self.time_left // 60, self.time_left % 60)
        self.ids.bsonoff.text = 'Backspace is ' + ('on' if self.lesson.backspace else 'off')
        self.ids.forced100.text = 'Forced Accuracy is ' + ('on' if self.lesson.forced100 else 'off')
        if self.lesson_clock:
            self.lesson_clock.cancel()
        self.lesson_clock = Clock.schedule_interval(lambda dt: self.clock_update(), 1)

    def pressed_letter(self, keyboard, ascii_tuple, letter, modifiers):
        if self.lesson.backspace:
            self.ids.redo.disabled = False

        if len(self.typed_letters) == len(self.lesson_letters):
            return

        if 'shift' in modifiers:
            letter = letter.upper() if letter not in self.symbols else self.corresp[self.symbols.index(letter)]
        elif 'capslock' in modifiers:
            letter = letter.upper() if 'shift' not in modifiers else letter

        if ascii_tuple[1] == 'backspace' and self.lesson.backspace and self.typed_letters:
            self.typed_letters = self.typed_letters[:-1]
        elif letter is not None and letter in self.acceptable_characters:
            letter_correct = letter == self.lesson_letters[len(self.typed_letters)]
            if letter_correct or not self.lesson.forced100:
                letter = '[color='+self.colors[
                    int(letter_correct)
                ]+']'+letter+'[/color]'
                self.typed_letters += [letter]

        self.on_screen_letters = self.typed_letters[-self.max_char_on_screen:]
        self.ids.typedText.text = ''.join(self.on_screen_letters) + ' ' * (
                self.total_char_width - len(self.on_screen_letters))

        if len(self.on_screen_letters) < self.max_char_on_screen:
            letters_to_show = self.lesson_letters[:self.total_char_width]
        elif len(self.typed_letters) > len(self.lesson_letters)-self.spaces_on_screen:
            letters_to_show = self.lesson_letters[
                              -(len(self.lesson_letters)-(len(self.typed_letters)-self.max_char_on_screen)):]
        else:
            starting_point = len(self.typed_letters) - self.max_char_on_screen
            if starting_point < 0:
                starting_point = 0
            letters_to_show = self.lesson_letters[
                              starting_point:starting_point+self.total_char_width]
        letters_to_show += [' ']*(self.total_char_width-len(letters_to_show))
        self.ids.givenText.text = ''.join(letters_to_show)

        self.ids.percentprogress.value = len(self.typed_letters)/len(self.lesson_letters)
        self.ids.percentcomplete.text = 'Percent complete: {:0>3.0%}'.format(self.ids.percentprogress.value)

        self.update_screen()

        if len(self.typed_letters) == len(self.lesson_letters):
            self.Exit()

    def clock_update(self):
        if len(self.typed_letters) == self.on_key_press:
            if self.seconds_without_key_presses < self.secondsOfIdleTimeAllowed:
                self.seconds_without_key_presses += 1
            else:
                self.file_idle_time += 1
        else:
            self.on_key_press = len(self.typed_letters)
            self.seconds_without_key_presses = 0

        self.time_left -= 1
        self.update_screen()

    def update_screen(self):
        total_letters = len(self.typed_letters)
        correct_letters = len(
            [letter for letter in self.typed_letters if self.colors[1] in letter])
        elapsed_time = self.total_time - self.time_left
        accuracy = calculate_accuracy(total_letters, correct_letters)
        real_wpm = calculate_real_wpm(total_letters, correct_letters, elapsed_time)
        raw_wpm = calculate_raw_wpm(correct_letters, elapsed_time)

        if accuracy >= 80:
            self.ids.accuracy.color = 0, 1, 1, 1
        elif self.accuracy >= 50:
            self.ids.accuracy.color = 1, .5, .5, 1
        else:
            self.ids.accuracy.color = 1, 0, 0, 1
        self.ids.clockThingThatTheyWant.text = time.strftime("%H:%M", time.localtime())
        self.accuracy = accuracy
        self.rawWPM = raw_wpm
        self.realWPM = real_wpm
        self.ids.accuracy.text = str(accuracy)
        self.ids.rawwpm.text = str(raw_wpm)
        self.ids.realwpm.text = str(real_wpm)
        self.ids.time.text = '{:0>2}:{:0>2}'.format(self.time_left // 60, self.time_left % 60)
        self.ids.idletime.text = '{:0>2}:{:0>2}'.format(self.file_idle_time // 60, self.file_idle_time % 60)

        if self.time_left == 0:
            self.Exit()

    def record_results(self):
        self.manager.results_object.add_new_result(
            part=self.lesson,
            accuracy=self.accuracy,
            wpm=self.realWPM,
            idle_time=self.file_idle_time
        )
        self.manager.results_object.totalFileIdleTime += self.file_idle_time
        self.manager.results_object.totalIdleTime += self.file_idle_time

    def Exit(self):
        self.keyboard.unbind(on_key_down=self.pressed_letter)
        self.keyboard = None
        self.lesson_clock.cancel()
        self.record_results()
        self.manager.current = 'Results'
        self.manager.get_screen('Results').update()
