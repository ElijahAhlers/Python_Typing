from copy import copy

def writeNewCSVFile(file, header, data):
    file = open(file,'w')
    file.write(','.join(header)+'\n\n')
    values = header
    for dic in data:
        writeStuff = ''
        for value in values:
            writeStuff+=str(dic[value])+','
        writeStuff = writeStuff[:-1]
        file.write(writeStuff+'\n')
    file.close()

def writeToCSVFile(file, listofthings):
    file = open(file,'a')
    [writeDic(file, dic) for dic in listofthings] if type(listofthings[0]) == type({}) else [writeLis(file, lis) for lis in listofthings]
    file.close()

def writeLis(openedfile, lis):
    openedfile.write(','.join(map(lambda x:str(x),lis))+'\n')

def writeDic(openedfile, dic):
    writeStuff = ''
    for key in dic.keys():
        writeStuff+=str(dic[key])+','
    writeStuff = writeStuff[:-1]
    openedfile.write(writeStuff+'\n')

def readCSVFile(file,withHeader=False):
    file = open(file,'r')
    filelist = ''.join([line for line in file]).split('\n')
    header = filelist[0].split(',')
    filelist = filelist[2:]
    filelist = [x.split(',') for x in filelist]
    if len(filelist[-1]) < 2:
        filelist = filelist[:-1]
    file.close()
    appendingdic = {}
    listofdicts = []
    for i,lis in enumerate(filelist,2):
        for value,key in map(lambda lis,header:(lis,header),lis,header):
            #print(key+'='+value)
            appendingdic[key] = value
        listofdicts.append(copy(appendingdic))
    if not withHeader:
        return listofdicts
    return header, listofdicts
