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

    def IdentifyKey(self, key, down):
        try:
            if key.char in self.listOfLetters:
                self.KeyPressMaster(key.char if (not self.shiftDownl) and (not self.shiftDownr) else key.char.upper())
            elif key.char in self.listOfNumbersAndSymbols:
                self.KeyPressMaster(key.char if (not self.shiftDownl) and (not self.shiftDownr) else self.listOfCorrespondingSymbols[self.listOfNumbersAndSymbols.index(key.char)])
            else:
                self.KeyPressMaster(key.char if (not self.capsToggle) or self.shiftDownl or self.shiftDownr else key.char.lower())
            
        except:
            if key == keyModule.space:
                self.KeyPressMaster(' ')
            elif key == keyModule.caps_lock:
                self.capsToggle = not self.capsToggle
            elif key == keyModule.shift:
                self.shiftDownl = True
            elif key == keyModule.shift_r:
                self.shiftDownr = True
            elif key == keyModule.backspace:
                self.KeyPressMaster('bspace')
            else:
                print(key)

    def makeKeyString(self):
        if len(self.onScreenText) > self.lettersOnScreen:
            self.onScreenText = self.onScreenText[1:]
            return [self.onScreenText, self.currentCursor+' '*(self.spacesOnScreen-1)]
        else:
            return [self.onScreenText, self.currentCursor+' '*(self.numOfLettersShownOnTheScreen-len(self.onScreenText)-1)]

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
            if self.bSpace and self.typedText:
                self.lettersTyped-=1
                self.lettersRight = self.lettersRight[:-1]
                self.typedText = self.typedText[:-1]
                self.onScreenText = self.onScreenText[:-1]
                if len(self.typedText) > len(self.onScreenText):
                    self.onScreenText = self.typedText[-len(self.onScreenText)-1] + self.onScreenText
        elif self.forced100:
            if key == self.wordsToType[self.lettersTyped]:
                self.lettersTyped+=1
                self.typedText+=key
                self.onScreenText+=key
                self.lettersRight.append(0)
#                try:
#                    self.lettersRight.append(0)
#                except:
#                    Exit()
            
                
        else:
            self.lettersTyped+=1
            self.typedText+=key
            self.onScreenText+=key
            try:
                self.lettersRight.append(0 if self.typedText[-1] == self.wordsToType[self.lettersTyped-1] else 1)
            except:
                self.Exit()
        self.ids.typedText.text = self.formatLetters(self.makeKeyString(),self.lettersRight[self.lettersTyped-self.lettersOnScreen:] if len(self.lettersRight)>self.lettersOnScreen else self.lettersRight)
        self.ids.givenText.text = self.makeLetterDisplayString()
        self.calculatePercent()
        self.ids.percentcomplete.text = self.addZeroesToPercent(self.percentComplete)
        self.ids.percentprogress.value = int(self.percentComplete)
        if self.lettersTyped == len(self.wordsToType):
            self.Exit()

    def formatLetters(self,letters,listOfColors):
        returnstr = []
        print(letters)
        for letter,color in map(lambda a,b:[a,b],letters[0],listOfColors):
            if letter == ' ':
                returnstr+=[' ']
            elif letter == '|':
                returnstr+=['|']
            elif letter == '"':
                returnstr+=['[color='+self.colors[color]+']\"[/color]']
            elif letter == '[':
                returnstr+=['[color='+self.colors[color]+']&br;[/color]']
            elif letter == ']':
                returnstr+=['[color='+self.colors[color]+']&bl;[/color]']
            else:
                returnstr+=['[color='+self.colors[color]+']'+letter+'[/color]']
        return ''.join(returnstr)+letters[1]
