def longest(lessons):
    longness = 0
    for lesson in lessons:
        longness = len(lesson) if len(lesson) > longness else longness
    return longness

def addSpaces(lesson,longness):
    return lesson+' '*(longness-len(lesson)) if longness>=len(lesson) else lesson[:longness]

def leftJustifyWithSpaces(lessons, greatestNumberOfCharactersYouWantInAnyGivenStringInTheListYouGaveMe):
    #greatestNumberOfCharactersYouWantInAnyGivenStringInTheListYouGaveMe = 33
    longness = longest(lessons)
    longness = longness if greatestNumberOfCharactersYouWantInAnyGivenStringInTheListYouGaveMe>=longness else greatestNumberOfCharactersYouWantInAnyGivenStringInTheListYouGaveMe
    for i in range(len(lessons)):
        lessons[i] = addSpaces(lessons[i],longness)
    return lessons

def addASpaceIfTheNumberIsLessThanTen(num):
    'This function does not work if you give it more than two digets or a negative number\nThis was coded for one specific purpose, so don\'t use it any other way.\nThanks!!'
    num = str(num)
    return num if len(num) == 2 else ' '+num