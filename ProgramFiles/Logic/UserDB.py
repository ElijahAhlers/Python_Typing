import csv
from Logic.CSVFuncs import readCSVFile as readCSV

def GetUsernamesAndPasswords():
    '''Reads Usernames and Passwords from their file and returns
    them as a list of dictionaries.  Each one looks like:
        OrderedDict([('Username',username), ('Password',password)])
    Parameters: None
    Returns: List of Dictionaries'''
    columns = ['Username','Password','Registered']
    file = open(open('Save Location.txt').read()+'UserData/UsernameAndPasswordHashed.csv','r')
    reader = csv.DictReader(file, fieldnames=columns)
    returningList = []
    for line in reader:
        returningList.append(line)
    return returningList[2:]
    

def GetRegisteredUsers():
    data = readCSV(open('Save Location.txt').read()+'UserData/UsernameAndPasswordHashed.csv')
    numOfItemsToTakeOff = -[x['Registered'] for x in data].count('0')
    data.sort(key=lambda x:x['Registered'], reverse=True)
    registered = data[:numOfItemsToTakeOff]
    return [x['Username'] for x in registered]

    
    
