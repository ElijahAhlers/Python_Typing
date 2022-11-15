from CSVFuncs import readCSVFile as read
from CSVFuncs import writeNewCSVFile as write
from CSVFuncs import writeToCSVFile as addToFile
import os
import hashlib

newUsers = read('newUsers.csv')
print(newUsers)
for firstName, lastName, username, password, registered in [item.values() for item in newUsers]:

    if username == 'auto':
        username = firstName.lower()+lastName.lower()

    password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    os.mkdir(username) if not os.path.exists(username) else None

    if not os.path.exists(username + '/data.csv'):
        write(username + '/data.csv', ['FirstName', 'LastName'], [{'FirstName': firstName, 'LastName': lastName}])

    current_users = read('UsernameAndPasswordHashed.csv')
    just_usernames = [dic['Username'] for dic in current_users]
    print(username, just_usernames)
    if username in just_usernames:
        print(current_users[just_usernames.index(username)])
        current_users[just_usernames.index(username)] = {'Username': username,
                                                         'Password': password,
                                                         'Registered': registered}
        print(current_users[just_usernames.index(username)])
    else:
        current_users += [{
            'Username': username,
            'Password': password,
            'Registered': registered
        }]
    write('UsernameAndPasswordHashed.csv', ['Username', 'Password', 'Registered'], current_users)
