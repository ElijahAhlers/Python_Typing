from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

from Logic.CSVFuncs import readCSVFile

import copy
import sys
import os

thing = '┴ ┐ └ ┬ ├ ─ ┼ │ ┤ ┘ ┌ ╞ ╪ ═ ╡'

def makeAsciiArtRow(date, day, accuracy, wpm, idleTime, sizes, lastOne=False):
    sideL, t, sideR = ('├','┼','┤') if not lastOne else ('└','┴','┘')
    bottom = sideL+'─'*sizes[0]+t+'─'*sizes[1]+t+'─'*sizes[2]+t+'─'*sizes[3]+t+'─'*sizes[4]+sideR
    mid = '│{0}│{1}│{2}│{3}│{4}│'.format(date+' '*(sizes[0]-len(date)),
                                   day+' '*(sizes[1]-len(day)),
                                   accuracy+' '*(sizes[2]-len(accuracy)),
                                   wpm+' '*(sizes[3]-len(wpm)),
                                   idleTime+' '*(sizes[4]-len(idleTime)))
    return mid+'\n'+bottom

def makeAsciiArtTop(sizes):
    return '┌{0}┬{1}┬{2}┬{3}┬{4}┐'.format(
        '─'*sizes[0],
        '─'*sizes[1],
        '─'*sizes[2],
        '─'*sizes[3],
        '─'*sizes[4])

def makeAsciiArtHeader(sizes):
    labels = ('Date','Day','Accuracy','Wpm','Idle Time')
    mid = '│'
    for label,size in map(lambda x,y:(x,y),labels,sizes):
        mid += label + ' '*(size-len(label)) + '│'
    bottom = '╞'
    for size in sizes:
        bottom += '═'*size + '╪'
    bottom = bottom[:-1] + '╡'
    return makeAsciiArtTop(sizes) + '\n' + mid + '\n' + bottom

def getBiggestSizes(stuff):
    copyOfStuff = copy.copy(stuff)
    returning = []
    for thing in copyOfStuff:
        thing.sort(key=len,reverse=True)
        returning += [len(thing[0])]
    return returning


def getSizes(data):
    header = ['Date','Day','Accuracy','Wpm','Idle Time']
    lists = []
    for i in range(5):
        newList = [header[i]]
        for lis in data:
            newList+=[lis[i]]
        lists+=[newList]
    return getBiggestSizes(lists)

def makeTheChart(data,sizes):
    header = makeAsciiArtHeader(sizes)
    on = 0
    last = len(data)-1
    body = ''
    for a,b,c,d,e in data:
        body += makeAsciiArtRow(a,b,c,d,e,sizes,lastOne=(on==last))+'\n'
        on+=1
    return header+'\n'+body
    


class TypingHistory(BoxLayout):
    
    def __init__(self,user,**kwargs):
        Builder.load_file('KivyGraphicFiles/TypingHistory.kv')
        print('self.ids is:', self.ids)
        super().__init__(**kwargs)
        self.username = user.username
        self.addTable(self.username)
        self.nextTics = 0
        self.previousTics = (len(self.makeListWithDict(self.username))//10)
        self.ids.name.text = 'History - '+self.username
        self.beginning = 0
        self.end = 9
        


    def exit(self):
        self.parent.parent.current = 'LessonSelectScreen'

    def addTable(self,username):
        testData = [['a','1','2','3','4'],['b','b','b','b','b']]
        chart = makeTheChart(self.makeListWithDict(self.username),self.sizes)
        self.ids.asciiArt.text = chart

    def makeListWithDict(self,username):
        allData = readCSVFile(str(open('Save Location.txt').read())+'UserData/'+username+'/history.csv')
        returnableList = []
        for dictionary in reversed(allData):
            returnableList.append([dictionary['Date'],dictionary['Lesson'],dictionary['Accuracy'],dictionary['WPM'],dictionary['Idle Time']])
        self.sizes = getSizes(returnableList)
        return returnableList

    def next(self):
        if self.nextTics:
            self.ids.goneTooFar.text = ''
            self.nextTics -= 1
            self.previousTics += 1
            self.beginning -= 10
            self.end -= 10
            chart = makeTheChart(self.makeListWithDict(self.username)[self.beginning:self.end],self.sizes)
            self.ids.asciiArt.text = chart
        else:
            self.ids.goneTooFar.text = "Woah There!!! That's the end!"
            

    def previous(self):
        if self.previousTics:
            self.ids.goneTooFar.text = ''
            self.nextTics += 1
            self.previousTics -= 1
            self.beginning += 10
            self.end += 10
            chart = makeTheChart(self.makeListWithDict(self.username)[self.beginning:self.end],self.sizes)
            self.ids.asciiArt.text = chart
        else:
            self.ids.goneTooFar.text = "Woah There!!! That's the end!"

    def refresh(self):
         self.addTable(self.username)
         self.nextTics = 0
         self.previousTics = (len(self.makeListWithDict(self.username))//10)
            
