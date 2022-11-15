from Logic.CSVFuncs import *
from Logic.FindWorstFile import findBestFile, bestOfFiles
from Logic.UserDB import GetRegisteredUsers
from Logic.UserClass import User
from datetime import date
import os
import pprint


class Results():

    def __init__(self,day,user):
        self.firstname = user.firstName
        self.lastname = user.lastName
        self.registered = user.registered
        print(self.registered)
        self.username = user.username
        self.name = day.lessonName
        self.todaysResults = []
        self.totalIdleTime = 0
        self.lastResultAdded = None

    def addResults(self, lessonName, accuracy, wpm, idleTimeInLesson):
        self.lastResultAdded = len(self.todaysResults)
        self.todaysResults += [{
            'name': lessonName,
            'accuracy': accuracy,
            'wpm': wpm,
            'idle time in lesson': idleTimeInLesson,
            'idle time in results window': 0
            }]
        
    def addIdleTimeFromResultsWindow(self, idleTimeInResultsWindow):
        self.todaysResults[self.lastResultAdded]['idle time in results window']=idleTimeInResultsWindow

    def recordReslus(self):
        #turns dictionary into list
        allLessons = [x for x in self.todaysResults]

        # formats lessons into (name, accuracy, wpm) tuples for finding best of files
        formattedLessons = [(self.todaysResults[x]['name'],
                             self.todaysResults[x]['accuracy'],
                             self.todaysResults[x]['wpm']
                             )for x in range(len(self.todaysResults))]

        #finds best files
        bestOfLessons = bestOfFiles(formattedLessons)
        
        
        todaysDate = date.today().strftime('%Y/%m/%d')
        todaysAccuracy = round(sum([a for x,a,x in bestOfLessons]) / len(bestOfLessons),0)
        todaysWPM = round(sum([a for x,x,a in bestOfLessons]) / len(bestOfLessons),0)
        todaysIdleTimeInLesson = sum([self.todaysResults[x]['idle time in lesson'] for x in range(len(allLessons))])
        todaysIdleTimeInResultsWindow = sum([self.todaysResults[x]['idle time in results window'] for x in range(len(allLessons))])
        todaysTotalIdleTime = self.totalIdleTime
        
        self.bool = True
#        self.printOutResults(self.firstname,
#                                self.lastname,
#                                todaysDate,
#                                todaysAccuracy,
#                                todaysWPM,
#                                todaysIdleTimeInLesson,
#                                todaysIdleTimeInResultsWindow,
#                                todaysTotalIdleTime,
#                                header=self.bool)
        data = [{'last name'                  : self.lastname,
                'first name'                  : self.firstname,
                'date'                        : todaysDate,
                'accuracy'                    : todaysAccuracy,
                'wpm'                         : todaysWPM,
                'idle time in lesson'         : todaysIdleTimeInLesson,
                'idle time in results screen' : todaysIdleTimeInResultsWindow,
                'total idle time'             : todaysTotalIdleTime}]
        if self.bool:
            self.bool = not self.bool

        file = str(open('Save Location.txt').read()+'CSVToGrade/'+self.name+'.csv')
        if os.path.exists(file):
            header, olddata = readCSVFile(file,withHeader=True)

            index = -1
            for dic in olddata:
                index += 1
                if (dic['last name'], dic['first name']) == (data[0]['last name'], data[0]['first name']):
                    if findBestFile(
                            [
                            ['0',float(dic['accuracy']), float(dic['wpm'])],
                            ['1',float(data[0]['accuracy']),float(data[0]['wpm'])]
                            ]
                    )[0] == '1':
                        olddata.pop(index)
                    else:
                        data = []
                    break
            data += olddata
            
        elif self.registered:
            registeredUsernames = GetRegisteredUsers()
            registeredUsernames.remove(self.username)
            blankData = [{
                          'last name'                   : User(username).lastName,
                          'first name'                  : User(username).firstName,
                          'date'                        : 0,
                          'accuracy'                    : 0,
                          'wpm'                         : 0,
                          'idle time in lesson'         : 0,
                          'idle time in results screen' : 0,
                          'total idle time'             : 0
                          } for username in registeredUsernames]
            data += blankData
        
        data.sort(key=lambda x:(x['last name'],x['first name']))
        
        writeNewCSVFile(file, [
                              'last name',
                              'first name',
                              'date',
                              'accuracy',
                              'wpm',
                              'idle time in lesson',
                              'idle time in results screen','total idle time'
                              ], data)

    def printOutResults(self,firstname,lastname,date,acc,wpm,iil,iir,total,header=True):
        if header:
            print(
"""
{:<12} | {:<10} | {:<20} | {:<8} | {:<8} | {:<8} | {:<8} | {:<8} |


""".format('First Name','Last Name','Date','Accuracy','WPM','Lesson','Results','Total'))
        print('{:<12} | {:<10} | {:<20} | {:<8} | {:<8} | {:<8} | {:<8} | {:<8} |'.format(firstname,lastname,date,acc,wpm,iil,iir,total))
