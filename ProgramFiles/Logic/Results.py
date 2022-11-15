from Logic.CSVFuncs import *
from Logic.FindWorstFile import findBestFile, bestOfFiles
from Logic.UserDB import GetRegisteredUsers
from Logic.UserClass import User
from datetime import date
import os


class Results:

    def __init__(self, day, user):
        self.firstname = user.firstName
        self.lastname = user.lastName
        self.registered = user.registered
        self.username = user.username
        self.name = day.lessonName
        self.todaysResults = []
        self.totalFileIdleTime = 0
        self.totalResultsIdleTime = 0
        self.totalIdleTime = 0
        self.lastResultAdded = None

    def addResults(self, lessonName, accuracy, wpm):
        self.lastResultAdded = len(self.todaysResults)

        if lessonName in [x['name'] for x in self.todaysResults]:
            lesson_index = [x['name'] for x in self.todaysResults].index(lessonName)
            if accuracy >= self.todaysResults[lesson_index]['accuracy']:
                if wpm >= self.todaysResults[lesson_index]['wpm']:
                    self.todaysResults[lesson_index] = {
                                                        'name': lessonName,
                                                        'accuracy': accuracy,
                                                        'wpm': wpm
                                                        }
        else:
            self.todaysResults += [{
                                    'name': lessonName,
                                    'accuracy': accuracy,
                                    'wpm': wpm
                                    }]

    def recordReslus(self):

        todaysDate = date.today().strftime('%Y/%m/%d')
        todaysAccuracy = round(sum([x['accuracy'] for x in self.todaysResults]) / len(self.todaysResults), 0)
        todaysWPM = round(sum([x['wpm'] for x in self.todaysResults]) / len(self.todaysResults), 0)

        data = [{'last name'                  : self.lastname,
                'first name'                  : self.firstname,
                'date'                        : todaysDate,
                'accuracy'                    : todaysAccuracy,
                'wpm'                         : todaysWPM,
                'idle time in lesson'         : self.totalFileIdleTime,
                'idle time in results screen' : self.totalResultsIdleTime,
                'total idle time'             : self.totalIdleTime}]

        file = str(open('Save Location.txt').read()+'CSVToGrade/'+self.name+'.csv')
        if os.path.exists(file):
            header, olddata = readCSVFile(file, withHeader=True)

            index = -1
            for dic in olddata:
                index += 1
                if (dic['last name'], dic['first name']) == (data[0]['last name'], data[0]['first name']):
                    if float(dic['accuracy']) < float(data[0]['accuracy']):
                        olddata.pop(index)
                    elif float(dic['accuracy']) == float(data[0]['accuracy']
                                                         ) and float(dic['wpm']) < float(data[0]['wpm']):
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
        
        data.sort(key=lambda x: (x['last name'], x['first name']))
        
        writeNewCSVFile(file, [
                              'last name',
                              'first name',
                              'date',
                              'accuracy',
                              'wpm',
                              'idle time in lesson',
                              'idle time in results screen',
                              'total idle time'
                              ], data)
