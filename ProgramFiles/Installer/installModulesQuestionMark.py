import sys
import os
def installModules():
    adminbat = '''
@echo off


runas /profile /user:clhs\\administrator "{0}\\Installer\\installModules.exe"'''.format(
    sys.path[0])

    with open('Installer/runAsAdmin.bat','w') as file:
        file.write(adminbat)
    command = '{0}\\Installer\\installModules.exe'.format(sys.path[0])
    os.system(command)
