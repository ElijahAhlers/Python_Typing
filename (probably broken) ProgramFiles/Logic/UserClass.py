from Logic.CSVFuncs import readCSVFile
from Logic.UserDB import GetRegisteredUsers
from os.path import exists as file_exists


class User:

    def __init__(self, username):
        user_file = open('Save Location.txt').read()+'UserData/'+username.lower()
        history_file = readCSVFile(user_file+'/history.csv') if file_exists(user_file+'/history.csv') else []
        datafile = readCSVFile(user_file+'/data.csv') if file_exists(user_file+'/data.csv') else []
        self.username = username
        self.historyDict = history_file
        self.historyPath = 'UserData/'+self.username+'/GamesHistory/GamesHistory.csv'
        data = None if len(datafile) < 1 else datafile[0]
        self.firstName = data['FirstName']
        self.lastName = data['LastName']
        self.registered = self.username in GetRegisteredUsers()
        del data
