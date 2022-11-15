from Logic.CSVFuncs import readCSVFile
from Logic.longestStringFunc import leftJustifyWithSpaces as lj



class Day():
    def __init__(self,LessonName, LessonLocation):
        self.files = readCSVFile(open('Save Location.txt').read()+
                        'TypingFiles/Lessons/'+LessonLocation+'.csv')
        lessonNames = readCSVFile(open('Save Location.txt').read()+
                        'TypingFiles/LessonList.csv')
        self.lessonlist = []
        self.lessonName = LessonName
        LessonName = ''.join([x+' ' if len(x) else '' for x in LessonName.split(' ')])[:-1]
        for num in range(len(lessonNames)):
            if lessonNames[num]['Name'] == LessonName:
                self.lessonNumber = num
                break
            
        #self.lessonNumber = 6

        for dic in self.files:
            self.lessonlist.append(
                Lesson(
                    open(open('Save Location.txt').read()+'TypingFiles/LessonParts/'+
                         dic['Lesson']+'.txt','r').read(),bool(int(dic['Backspace'])),
                    bool(int(dic['Forced100'])), int(dic['Time']), dic['Lesson'], int(dic['Part'])
                    ))
        self.numOfLessons = len(self.lessonlist)
                    
            
class Lesson():
    def __init__(self, text, bspacemode, forced100, time, filename, part):
        self.text = text
        self.backspace = bspacemode
        self.forced100 = forced100
        self.time = time
        self.filename = filename
        self.part = part-1
