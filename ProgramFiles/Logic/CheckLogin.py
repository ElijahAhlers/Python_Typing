from Logic import UserDB as udb
import hashlib

def CheckCreds(username,password):
    '''Checks data entered in Username and password on the login screen.
    Parameters: (string,string)
    Returns: Boolean Authenticate, Current User'''
    UserData = udb.GetUsernamesAndPasswords()
    Authenticate = False
    for dictionary in UserData:
        if username == dictionary["Username"]:
            if hashlib.sha256(password.encode('utf-8')).hexdigest()==dictionary["Password"]:
                Authenticate = True
                return Authenticate,username
            
    return False
        
            
