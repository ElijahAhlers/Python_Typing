#Built into python
import threading as th
from functools import partial
import copy

#Kivy stuff
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown

#Stuff we made
import Logic.CSVFuncs as ce
from Logic.LessonClass import Day as MakeDay
from Logic.longestStringFunc import leftJustifyWithSpaces as lj
from Logic.Results import Results
from Logic.longestStringFunc import addASpaceIfTheNumberIsLessThanTen as addSpace
#from Logic.longertString

Window.borderless = True


class CustomDropDown(BoxLayout):
      def chooseLesson(self,selected_button,accualTitleWithoutSpaces):
            reader = ce.readCSVFile(self.parent.parent.parent.parent.parent.location + '/TypingFiles/LessonList.csv')
            self.parent.parent.parent.parent.parent.activeDay = MakeDay(accualTitleWithoutSpaces, reader[selected_button]['Location'])
            self.parent.parent.parent.parent.parent.resultsObject = Results(self.parent.parent.parent.parent.parent.activeDay,self.parent.parent.parent.parent.parent.activeUser)
            self.parent.parent.parent.parent.parent.nextLesson = 0
            self.parent.parent.parent.parent.parent.MakeTypingWindow()
            self.parent.parent.parent.parent.parent.current = 'TypingWindow'


class HomeWindow(GridLayout):
      
      def __init__(self,user,**kwargs):
            Builder.load_file('KivyGraphicFiles/TypingHome.kv')
            self.user = user
            self.builddadropdown()
            super(HomeWindow, self).__init__(**kwargs)
            self.fillinstats()

      def chooseLesson(self,selected_button):
            reader = ce.readCSVFile(self.parent.parent.location+
                                    '/TypingFiles/LessonList.csv')
            selected_button = selected_button if not selected_button == '<nextlesson>' else reader[0]['Name']
            self.parent.parent.activeDay = MakeDay(selected_button,
                                          reader[[x['Name'] for x in reader].index(
                                                selected_button)]['Location'])
            self.parent.parent.resultsObject = Results(self.parent.parent.activeDay,self.parent.parent.activeUser)
            self.parent.parent.nextLesson = 0
            self.parent.parent.MakeTypingWindow()
            self.parent.parent.current = 'TypingWindow'
      
      def fillinstats(self):
            try:                  
                  yesterdayStats = ce.readCSVFile(str(open('Save Location.txt').read())+'UserData/'+self.user.username+'/history.csv')
                  if len(yesterdayStats) > 0:
                        yesterdayStats = yesterdayStats[-1]
                  else:
                        yesterdayStats['Lesson'] = 'Spacebar and Home Row'
                  self.ids.lastlesson.text = 'Last time, you typed '+str(''.join([x+' ' if len(x) else '' for x in yesterdayStats['Lesson'].split(' ')])[:-1])
                  self.ids.accuracy.text = str(yesterdayStats['Accuracy']+'%')
                  self.ids.wpm.text = str(yesterdayStats['WPM'])
                  self.ids.idleTime.text = str(yesterdayStats['Idle Time'])
                  self.ids.nextlesson.text = self.findNextLesson(yesterdayStats['Lesson'])
            except:
                  pass
                  

      def findNextLesson(self,yesterdayLesson):
            yesterdayLesson = ''.join([x+' ' if len(x) else '' for x in yesterdayLesson.split(' ')])[:-1]
            lessonlist = ce.readCSVFile(str(open('Save Location.txt').read())+'/TypingFiles/LessonList.csv')
            todaylesson = ''
            todaylesson = 0
            for i in range(len(lessonlist)):
                  if lessonlist[i]['Name'] == yesterdayLesson:
                        todaylesson = i+1
                        break
                  else:
                        pass                  
            return lessonlist[todaylesson]['Name']

      def builddadropdown(self):
            rawdata = ce.readCSVFile(open('Save Location.txt').read()+'TypingFiles/LessonList.csv')
            lessons = [list(x.values())[0] for x in rawdata]
            lessonNum = 0
            dropdownFoundation='''
<CustomDropDown>
      DropDown:

            id: dropdown
            on_parent: self.dismiss()
            #on_select: btn.text = '{}'.format(args[1])
            auto_dismiss: False
            min_state_time: 9999999999
            auto_width: False
            width: 350
'''
            lessonsWithSpaces = lj(copy.copy(lessons),32)
            for i in range(len(lessons)):
                  lessonNum+=1
                  dropdownFoundation+="""
            Button:
                  text: '{0}{1}'
                  size_hint_y: None
                  height: '25dp'
                  on_press: root.chooseLesson({2},'{3}')
""".format('Lesson '+str(addSpace(lessonNum))+': ',lessonsWithSpaces[i],i,lessons[i])
                  
            Builder.load_string(dropdownFoundation)
      
      def ExitButton(self):
            print('at lest you tried')
            self.parent.parent.parent.parent.parent.close()

      def changePassword(self):
            self.parent.parent.ChangePassword()
            self.parent.parent.current = 'ChangePasswordScreen'

      def Games(self):
            self.parent.parent.GamesMenu()
            self.parent.parent.current = 'Games Menu'
            Window.fullscreen = 'auto'

      def typingHistory(self):
            self.parent.parent.TypingHistory()
            self.parent.parent.current = 'TypingHistory'
            
         


