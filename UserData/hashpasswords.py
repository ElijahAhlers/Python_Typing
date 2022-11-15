from CSVFuncs import writeNewCSVFile as write
from CSVFuncs import readCSVFile as read
from pprint import pprint
import hashlib

data = read('UsernameAndPassword.csv')
pprint(data)
print('\n\n')
    
for dic in data:
    dic['Password'] = hashlib.sha256(dic['Password'].encode('utf-8')).hexdigest()

pprint(data)

write('UsernameAndPasswordHashed.csv',['Username','Registered','Password'],data)
    
    
