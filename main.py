#Roshan Nair
#rsnair
#Term Project - Voice Modulation

#-------------------------IMPORTS-------------------------

#Main Modules
import numpy
import scipy
import math
import winsound
import pyaudio
import wave
import random
import matplotlib
from Tkinter import *
from PIL import ImageTk
import speech_recognition

#Key Functions from scipy module for wave file reading, writing
from scipy.io.wavfile import read
from scipy.io.wavfile import write

#Comtypes module for generating artificial voice
from comtypes.gen import SpeechLib
from comtypes.client import CreateObject

#-------------------------Audio/Wav Functions--------------------------

#Comtypes for artifical voice
#Modified to work with wav files and custom strings from Stackoverflow source
#http://stackoverflow.com/questions/15516572
#/how-can-i-convert-text-to-speech-mp3-file-in-python
def stringToWav(s,fileName):
    #Default bit rate is 22050
    engine = CreateObject("SAPI.SpVoice")
    stream = CreateObject("SAPI.SpFileStream")
    stream.Open(fileName, SpeechLib.SSFMCreateForWrite)
    engine.AudioOutputStream = stream
    engine.speak(s)
    stream.Close()

#Followed from powerpoint how to use scipy
#Modified to fit my code
#http://www.slideshare.net/mchua/sigproc-selfstudy-17323823
def getWavData(fileName):
    data = scipy.io.wavfile.read(fileName)
    return data[1]
def writeWavFile(wavData,fileName,bitrate = 22050):
    scipy.io.wavfile.write(fileName,bitrate,wavData)    
def getBitRate(fileName):
    data = scipy.io.wavfile.read(fileName)
    return data[0]
def makeGraph(wavFileName,imgFileName,fourier=False):
    data = getWavData(wavFileName)
    matplotlib.pyplot.clf()
    maxX = 50000
    maxY = 2.5*(10**12)
    minX = 0
    minY = -maxY
    if fourier:
        data = numpy.fft.rfft(data)   
        axes = matplotlib.pyplot.gca()
        if "artificial" in wavFileName:
            maxY = 2*(10**6)
            minY = -maxY
        axes.set_xlim([minX,maxX])
        axes.set_ylim([minY,maxY])
    matplotlib.pyplot.plot(data)
    matplotlib.pyplot.savefig(imgFileName)
    
#Record input from microphone for given amount of seconds
#Modified from pyaudio documentation website and stackoverflow website
#https://people.csail.mit.edu/hubert/pyaudio/docs/
#http://stackoverflow.com/questions/892199/detect-record-audio-in-python
def recordAudio(seconds,fileName,bitRate = 22050*2):
    #return
    chunk = 1024 #number of samples in stream
    numChannels = 1 #stereo
    formatPyaudio = pyaudio.paInt32 #4 bytes
    audioInstance = pyaudio.PyAudio()
    stream = audioInstance.open(format = formatPyaudio, channels = numChannels,
                                rate = bitRate, input=True,
                                frames_per_buffer=chunk)
    print("Starting Recording for %d seconds!") %(seconds)    
    frames = []    
    for i in range(0, int(bitRate/chunk*seconds)):
        data = stream.read(chunk) #Note! Encodes into string
        frames.append(data)
    print("Finished Recording!")
    
    stream.stop_stream() #Close stream for microphone
    stream.close()
    audioInstance.terminate()
    
    #Using wave module creates wav file
    waveFile = wave.open(fileName, 'wb')
    waveFile.setnchannels(numChannels)
    waveFile.setsampwidth(audioInstance.get_sample_size(formatPyaudio))
    waveFile.setframerate(bitRate)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    
#Use winsound to play wav file
#From winsound documentation
#https://docs.python.org/2/library/winsound.html
def playWav(fileName):
    winsound.PlaySound(fileName,winsound.SND_FILENAME)

#Take wave file, change volume and rewrite
def changeVolume(fileName,multiplier=2,newFileName = None):
    if (newFileName==None):
        newFileName = fileName
    data = getWavData(fileName)
    for i in range(len(data)):
        data[i] = data[i]*multiplier
    bitRate = getBitRate(fileName)
    writeWavFile(data,newFileName,bitRate)

#-------------------------------Primary Algorithms----------------------------

#Helper function for fourierTranform
#Loops through lists and multiplies contents of each and then adds them
#Essentially dot product with lists instead of vectors
def addEachElement(transform,wavData):
    newList = []
    for i in range(len(transform)):
        summer = 0
        for dataIndex in range(len(wavData)):
            summer+=transform[i][dataIndex]*wavData[dataIndex]
        newList.append(summer)
    return newList    
    
#Applies fourier transformation for waveData
#https://www.youtube.com/watch?v=6-llh6WJo1U#t=551.314916
#Video discusses fourier transformation math link from there as well
def fourierTransform(wavData):   
    fundamentalFrequency = -2*math.pi
    dimensions = wavData.shape
    rowLength = dimensions[0]
    if (rowLength>30): #To prevent long lengths of wavData as it not optimized
        return None    #yet.        
    #wavData = numpy.asarray(wavData, dtype=float) #Convert wave data into
                                                  #numpy array    
    newList = numpy.arange(rowLength) #act as summation from 0 to rowLength-1
    k = newList.reshape((rowLength, 1)) #k in formula
    fourierTransformationExponent = (1j*fundamentalFrequency*k
                                    *newList/rowLength)
    transform = numpy.exp(fourierTransformationExponent) #e to the exponent
    resultList = addEachElement(transform,wavData)
    return numpy.asarray(resultList) #change into numpy array

#same formula as above except with positive fundamental frequency...
def inverseFourierTransform(wavData):    
    fundamentalFrequency = 2*math.pi
    dimensions = wavData.shape
    rowLength = dimensions[0]
    newList = numpy.arange(rowLength)
    k = newList.reshape((rowLength, 1))
    fourierTransformationExponent = (1j*fundamentalFrequency*k
                                    *newList/rowLength)
    transform = numpy.exp(fourierTransformationExponent)
    resultList = addEachElement(transform,wavData)
    return numpy.asarray(resultList)

def lengthOfMaxPeaks(wavFileName,peakIndexList):
    data = getWavData(wavFileName)
    sizeList = []
    for element in peakIndexList:
        startValue = element
        counter=0
        for value in data[element-10:0:-5]: #Jump through left values
            counter+=1
            if epsilonEqual(getSlope(5,value,startValue),0,1):
                print(element,"For Left at",element-counter)
                leftValue = element-counter
                break
            startValue = value
        startValue = element
        counter = 0
        for value in data[element+10:len(data)-1:5]: #Right Values
            counter+=1
            if epsilonEqual(getSlope(5,value,startValue),0,1):
                print(element,"For Right at",element+counter)
                rightValue = element+counter
                break    
            startValue = value
        sizeList.append(rightValue-leftValue)
    print("Main Equality",len(sizeList)==len(peakIndexList))
    return sizeList
    
def subtractSameLenList(list0,list1): #Assumes same length of list
    newList = []
    for i in range(len(list0)):
        newList.append(abs(list0[i]-list1[0]))
    print("NewList",newList)
    return newList

def numberOfSizeDiscrep(arrayList):
    threshold = 4000
    counter = 0
    index = -1
    indexList = []
    for size in arrayList:
        index+=1
        if (size>threshold):
            counter+=1
            indexList.append(index)
    print("Counter",counter)
    return (counter,indexList)
    
def analysisMessage(data):
    data.analysisMessage="Could not recognize the word."
    data.analysisMessage+="\nTry listening to the pronounciation again.\n"
    data.analysisMessage+="Or try to speak louder with less outside noise."
    differencePeaks = abs(data.numPeaksUser-data.numPeaksAI)
    if (not data.success):
        return        
    elif (differencePeaks==0):
        differenceSizeList = subtractSameLenList(data.userVoiceSizeList,
                                                 data.artificialVoiceSizeList)
        numDiscrep,indexList = numberOfSizeDiscrep(differenceSizeList)
        if numDiscrep<2:
            data.analysisMessage= "Excellent Work! You pronounced the word"
            data.analysisMessage+= " perfectly!\nNow try another word!"
        else:            
            data.analysisMessage = (
            "You are elongating or shortening certain vowels.\nWork on these ")
            print("Errorry indexList",indexList)
            print("Vowel List",data.vowelList)
            counter = 0
            temp = ""
            if len(indexList)==0:
                data.analysisMessage = "Put a little more stress on "
                data.analysisMessage+= "each vowel.\nYour syllables "
                data.analysisMessage+= "aregetting blurred together."
                return
            for index in indexList:
                if (index>=len(data.vowelList)):
                   data.analysisMessage = "You adding unecessary stresses on "
                   data.analysisMessage+= "the last syllables."
                   return
                   
                val = data.vowelList[index]
                temp+="%s " %(val)
                counter+=1
            temp = removeDigits(temp)
            data.analysisMessage+=temp
    elif (data.numPeaksUser>data.numPeaksAI):
        
        data.analysisMessage = (
    "Smooth out your voice.\nRight now you are very jumpy with each syllable")
    elif(data.numPeaksUser<data.numPeaksAI):
        if epsilonEqual(data.userVoiceSizeList[0],
                        data.userVoiceSizeList[0],2000):
            counter = 0
            aiIndex = 0
            for index in range(1,len(data.userVoiceSizeList)):
                try:
                    if (epsilonEqual(
                        data.artificialVoiceSizeList[aiIndex][aiIndex]+1,
                        data.userVoiceSizeList[index],2000)):
                        counter+=1
                        if (counter==2):
                            data.analysisMessage = "Excellent Work!"
                            return
                except:
                    differenceSizeList = subtractSameLenList(
                        data.userVoiceSizeList,data.artificialVoiceSizeList)
                    numDiscrep,indexList = numberOfSizeDiscrep(
                                                        differenceSizeList)
                    data.analysisMessage = (
            "You are elongating or shortening your vowels.\nWork on these ")
                    counter = 0
                    temp = ""
                    print("Vowel List",data.vowelList)
                    print("Errorry indexList",indexList)
                    if len(indexList)==0:
                        data.analysisMessage = "Put a little more stress on "
                        data.analysisMessage+= "each vowel.\nYour syllables "
                        data.analysisMessage+= "are getting blurred together."
                        return
                    for index in indexList:
                        if (index>=len(data.vowelList)):
                            data.analysisMessage = "You adding unecessary"
                            data.analysisMessage+= " stresses on "
                            data.analysisMessage+= "the last syllables."
                            return
                        temp+="%s " %(data.vowelList[index])
                        print("Key Counter",counter)
                        counter+=1
                    temp = removeDigits(temp)
                    data.analysisMessage+=temp
                    return
                    
def isMaxOfSurrounding(wavData,index,userFlag):
    if (userFlag):
        offset = 2000
    else:
        offset = 500

    partialList = numpy.asarray(wavData[index-offset:index+offset+1])
    #print(partialList.max())
    if (len(partialList)==0):
        return -999999
    return partialList.max()
   

def numberOfVowels(data,pronounceString):
    data.vowelList = []
    pronounceString.strip()
    pronounceList = pronounceString.split(" ")
    counter = 0
    for phone in pronounceList:
        if (phone[0] in "AEIOUaeiou"):
            counter+=1
            data.vowelList.append(phone)
    return counter

#From speech_recognition website documentation (modified)
#https://github.com/Uberi/speech_recognition/blob/master/examples/
#audio_transcribe.py
def recognizeText(fileName):
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.AudioFile("userVoice.wav") as source:
        audio = recognizer.record(source)
    
    try:
        return recognizer.recognize_google(audio).lower()
    except speech_recognition.UnknownValueError:
        return None
    except speech_recognition.RequestError:
        return None   
    
def numOfPeaks(wavData,threshold,userFlag):
    total = 0
    counter = 0
    numPeaks = 0
    digit = 0
    indexList = []
    for element in wavData:
        total+=element
        counter+=1
        average = total/counter
        if (abs(element-average)>threshold and 
            element == isMaxOfSurrounding(wavData,counter,userFlag)):
            indexList.append(counter)
            digit+=1
            numPeaks+=1
    print("counter",counter)
    return (numPeaks,indexList)

def extraLetters(originalPhone,typeOf):
    if (originalPhone=="AO"):
        return "ow"
    elif (typeOf=="vowel"):
        if ("A" in originalPhone):
            if ("E" in originalPhone):
                return originalPhone[0]+"ye"
            return originalPhone+"h"
        elif ("E" in originalPhone):
            if (originalPhone=="EH"):
                return originalPhone
            elif(originalPhone=="ER"):
                return "H"+originalPhone
            if (originalPhone=="EY"):
                return originalPhone.lower()+"e"
        elif("I" in originalPhone):
            if (originalPhone=="IH"):
                return "heeh"
            elif(originalPhone=="IY"):
                return "ee"
        elif("O" in originalPhone):
            return originalPhone     
        elif("U" in originalPhone):
            if (originalPhone=="UH"):
                return "huh"
            return "hoo"
        else:
            return originalPhone[0]+originalPhone
    elif (typeOf=="stop" or typeOf=="fricative" or typeOf=="affricate" or
          typeOf=="liquid" or typeOf=="semivowel" or typeOf=="aspirate"):
        if ("D" in originalPhone and "H" in originalPhone):
            return "dhah"
        elif(originalPhone=="HH"):
            return originalPhone[0]+"uh"
        elif(originalPhone=="JH"):
            return "juh"
        elif("S" in originalPhone):
            return originalPhone+"ah"
        elif(originalPhone=="TH"):
            return "thaah"
        elif(originalPhone=="Y" or originalPhone=="Z"):
            return originalPhone+"ah"
        elif(originalPhone=="ZH"):
            return "Zhaah"
        return originalPhone+"uh"
    elif(typeOf=="nasal"):
        if ("G" in originalPhone):
            return "i"+originalPhone
        else:
            return originalPhone+"uh"    
    else:
        return originalPhone

def playPronounciation(data):
    phoneticText = readFile("cmudict.phones")
    phoneticList = phoneticText.split("\n")
    onlyPhones = []
    temp = ""
    indexList = []
    for letter in data.currentPronounce:
        if (not letter.isdigit()):
            temp+=letter            
    listOfCurrentPronounce = temp.split(" ")                
    for line in phoneticList:
        lineList = line.split("\t")
        onlyPhones.append(lineList[0])        
    for phonetic in listOfCurrentPronounce:
        index = onlyPhones.index(phonetic)
        indexList.append(index)
    soundOutPhones(data,indexList,True)
    #playWav("artificialVoice.wav")
    
    
def createFullPhoneSound(data,arrayList,boolean):
    if boolean:
        arrayList.append(getWavData("artificialVoice.wav"))
    else:
        arrayList.append(getWavData("artificialVoiceSent.wav"))
    tupleOfPhones = tuple(arrayList)
    newData = numpy.concatenate(tupleOfPhones)
    writeWavFile(newData,"fullPhoneticSound.wav",
                 data.scalePronounceBeforeValue*getBitRate(
                 "phoneticSound0.wav"))

    
def soundOutPhones(data,indexList,boolean):
    fullText = readFile("cmudict.phones")
    phoneticList = fullText.split("\n")
    phoneticSoundIndex = 0
    phoneticSoundList = []
    for index in indexList:
        line = phoneticList[index]
        lineList = line.split("\t")
        newPhone = extraLetters(lineList[0],lineList[1])
        phoneFileName = "phoneticSound%d.wav" %(phoneticSoundIndex)
        stringToWav(newPhone,phoneFileName)
        wavData = getWavData(phoneFileName)
        wavData = removeTrailingZeros(wavData)
        wavData = removeLeadingZeros(wavData)
        phoneticSoundList.append(wavData)
        writeWavFile(wavData,phoneFileName)
        phoneticSoundIndex+=1
    createFullPhoneSound(data,phoneticSoundList,boolean)
    playWav("fullPhoneticSound.wav")

def pronounceSent(data):
    print("Hello")
    data.currentSentence = data.entryTextSent.get().lower()
    if data.currentSentence == "":
        return
    sentenceList = data.currentSentence.split(" ")
    
    dictList = generateWordAndPronounceList()
    onlyWord = []
    stringToWav(data.currentSentence,"artificialVoiceSent.wav")
    phoneticText = readFile("cmudict.phones")
    phoneticList = phoneticText.split("\n")
    for element in dictList:
        noSpace = element.split(" ")
        onlyWord.append(noSpace[0])
    dictIndex = []
    for word in sentenceList:
        dictIndex.append(onlyWord.index(word))
    pronounceList = []
    for index in dictIndex:
        pronounceList.append(dictList[index].split(" ")[1:])
    print(pronounceList)
    temp = ""
    for indivPronounceList in pronounceList:
        for fullThing in indivPronounceList:
            for letter in fullThing:
                if (not letter.isdigit()):
                    temp+=letter
            temp+=" "
    temp = temp[:-1]
    pronounceList = temp.split(" ")
    onlyPhones = []
    indexList = []
    for line in phoneticList:
        lineList = line.split("\t")
        onlyPhones.append(lineList[0])        
    for phonetic in pronounceList:
        index = onlyPhones.index(phonetic)
        indexList.append(index)
    soundOutPhones(data,indexList,False)
    
#---------------------------Secondary Algorithms/Functions-----------------
    
#From 15-112 notes to read files
#http://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()
        
def removeDigits(s):
    newString = ""
    for character in s:
        if (not character.isdigit()):
            newString+=character
    return newString
        
#Slow down or speed up wave file depending on multiplier >1 or <1
def changeWavFileSpeed(originalFileName,newFileName,multiplier):
    data = getWavData(originalFileName)
    bitRate = getBitRate(originalFileName)
    newValue = int(bitRate*multiplier)
    print(newValue)
    writeWavFile(data,newFileName,newValue)
        
#Some bug in wavData transformtaion WORKINPROGRESS
def changeFrequency(wavData,modulationAdder):
    for i in range(len(wavData)):
        wavData[i][0] = wavData[i][0]+modulationAdder
    return wavData

#Parse through CMU word dictionary
def generateWordAndPronounceList():
    fullString = readFile("cmudict.dict")
    stringList = fullString.split("\n")
    return stringList

#Get random word from the dictionary
def getRandomWordAndPronounce(wordList):
    firstWord = "0"
    while (not firstWord.isalpha()):
        randomNumber = random.randint(0,len(wordList))
        s = wordList[randomNumber]
        index = s.find(" ")
        firstWord = s[:index]
    return s

#Split the word and its pronounciation
def getWordPronounceTuple(fullString):
    index = fullString.find(" ")
    if (index==-1):
        return None
    wordString = fullString[:index]
    pronounceString = fullString[index+1:]
    return (wordString,pronounceString)

#Change stresses into either primary or secondary
def modifyPronounceStress(data):
    temp = ""
    for character in data.currentPronounce:
        if character.isdigit():
            if (character=="1"):
                temp+="(PS)"
            elif(character=="2"):
                temp+="(SS)"
            else:
                temp+="(NS)"
        else:
            temp+=character
    data.currentPronounceStress = temp

def removeLeadingZeros(array):
    for i in range(len(array)):
        if not epsilonEqual(array[i],0.0,1):
            newArray = numpy.asarray(array[i:])
            break
    return newArray

def removeTrailingZeros(array):
    for i in range(len(array)-1,-1,-1):
        if not epsilonEqual(array[i],0.0,1):
            newArray = numpy.asarray(array[:i+1])
            break
    return newArray

#Get a random word an pronounce and AI speak it into a wav file
def initiateWordandPronounce(data,flag=True):
    if flag:
        randomWordandPro = getRandomWordAndPronounce(data.allWordList)
    else:
        randomWordandPro = data.typedWord
    (data.currentWord,data.currentPronounce)=getWordPronounceTuple(
                                             randomWordandPro)
    modifyPronounceStress(data)
    stringToWav(data.currentWord,"artificialVoice.wav")
    
def getSlope(deltaX,y0,y1):
    return abs(y0-y1)/float(deltaX)

def epsilonEqual(val0,val1,epsilon):
    if (abs(val0-val1)<epsilon):
        return True
    else:
        return False
        
def determineSucess(data):
    word = recognizeText("userVoice.wav")   
    data.success = False
    if(word!=None and word==data.currentWord):
        data.success = True
    print("Success",data.success)
    
#--------------------Tkinter event or init calls----------------------------
#Initialize the graphs for both AI voice and user voice
def initiateAnalysisGraph(data):
    imageAITime = ImageTk.PhotoImage(file="artificialVoice.png")
    imageUserTime = ImageTk.PhotoImage(file="userVoice.png")
    data.imageAITime = imageAITime
    data.imageUserTime = imageUserTime
    imageAIFreq = ImageTk.PhotoImage(file="artificialVoice(fft).png")
    imageUserFreq = ImageTk.PhotoImage(file="userVoice(fft).png")
    data.imageAIFreq = imageAIFreq
    data.imageUserFreq = imageUserFreq
    
def loadImage(data):
    imageIcon = ImageTk.PhotoImage(file="speakIcon.png")
    imageScreenShot0 = ImageTk.PhotoImage(file="screenshot0.png")
    imageScreenShot1 = ImageTk.PhotoImage(file="screenshot1.png")
    data.imageIcon = imageIcon
    data.imageScreenShot0 = imageScreenShot0
    data.imageScreenShot1 = imageScreenShot1
    
#Get word only without pronounciation
def getWordOnly(string):
    firstSpaceIndex = string.find(" ")
    return string[:firstSpaceIndex]

#Since cmuDict is sorted by alphabet, can find quicker
def searchForWord(data):
    data.onlyWordList = list(map(getWordOnly,data.allWordList))
    try:
        index = data.onlyWordList.index(data.entryString)
        return index
    except:
        print("Didn't type anything!")

def getEntryText(data):
    data.entryString = data.entryText.get()
    if (len(data.entryString.strip())==0):
        return
    #if (" " in data.entryString):
        #stringToWav(data.entryString,"tempSentence.wav")
        #playWav("tempSentence.wav")
    else:
        index = searchForWord(data)
        if (index==-1):
            return
        else:
            data.typedWord = data.allWordList[index]
            initiateWordandPronounce(data,False)
    data.entryText.delete(0,len(data.entryString))

#Button call for Instruction screen
def callInstruction(data):
    data.originalScreen = data.screen
    data.screen="instruction"

def callSentence(data):
    data.screen="sentences"
    
def callSentencePronounce(data):
    data.originalScreen = data.screen
    data.screen = "sentencesPronounce"
    print("hit")
#Button call to main screen
def callBegin(data):
    data.originalScreen = data.screen
    data.screen="begin"
    data.instructionButton.configure(bg="steel blue")
    initiateWordandPronounce(data)

#Button call for back
def callBack(data):
    if data.originalScreen == "welcome":
        data.instructionButton.configure(bg="indian red")
    (data.screen,data.originalScreen) = (data.originalScreen,data.screen)

#Button call for pronounce screen
def callPronounce(data):
    data.originalScreen = data.screen
    data.screen = "pronounce"
            
#Button call to start recording
#352kbps - AI
#1411kbps - User
def startRecording(canvas,data):
    data.originalScreen = data.screen
    data.recordButton.configure(bg="red")
    canvas.delete(ALL)
    redrawAll(canvas, data)
    canvas.update()
    data.recordButton.configure(bg="steel blue")
    recordAudio(3,"userVoice.wav")
    data.screen = "analysis"
    data.artificialFourier = numpy.fft.rfft(getWavData("artificialVoice.wav"))
    data.userFourier = numpy.fft.rfft(getWavData("userVoice.wav"))
    
    makeGraph("artificialVoice.wav","artificialVoice.png")
    makeGraph("userVoice.wav","userVoice.png")
    makeGraph("artificialVoice.wav","artificialVoice(fft).png",True)
    makeGraph("userVoice.wav","userVoice(fft).png",True)
    data.numVowels = numberOfVowels(data,data.currentPronounce)
    (data.numPeaksUser,data.indexListUser) = numOfPeaks(
                                    getWavData("userVoice.wav"),
                                            500000000,True)
    #numPeaksUser-=1 In case microphone has faulty peak in beginning
    print("____________________________")
    (data.numPeaksAI,data.indexListAI) = numOfPeaks(getWavData(
                                        "artificialVoice.wav"),
                                        5000,False)
    data.userVoiceSizeList = lengthOfMaxPeaks("userVoice.wav",
                                              data.indexListUser)
    data.artificialVoiceSizeList = lengthOfMaxPeaks("artificialVoice.wav",
                                                    data.indexListAI)
    for i in range(len(data.artificialVoiceSizeList)):
        data.artificialVoiceSizeList[i]=data.artificialVoiceSizeList[i]*(float(
        140000)/30000)
    print(data.userVoiceSizeList)
    print(data.artificialVoiceSizeList)
    
    print("numVowel =",data.numVowels)
    print("numPeaksUser =",data.numPeaksUser)
    print("numPeaksAI =",data.numPeaksAI)
    determineSucess(data)
    analysisMessage(data)

def startPronounce(data):
    playPronounciation(data)
           
    
def switchGraphState(data):
    if (data.showTime):
        data.graphSwitchButton.configure(text="Show Time Domain")
        data.showTime = not data.showTime
    else:
        data.graphSwitchButton.configure(text="Show Frequency Domain")
        data.showTime = not data.showTime
    
def changeHelp(data,hoverBool,message=None):
    if (hoverBool):
        data.helpMessage = message
    else:
        data.helpMessage = data.helpMessageOriginal

def callWelcomeBack(data):
    data.screen="welcome"


    
#-------------------------------GUI Instructions------------------

#Draw splash screen
def drawWelcome(canvas,data):
    fontSize = 60
    heightScale = 0.2
    heightMargin = data.height*heightScale
    canvas.create_rectangle(0,0,data.width,data.height,fill="chocolate2")
    canvas.create_text(data.width//2,data.height//2-heightMargin,
                       text = "Welcome to SpeakIt!",
                       font="MSerif %d" %(fontSize),
                       anchor = S,fill="black")
    canvas.create_window(0,data.height,window=data.instructionButton,anchor=SW)
    canvas.create_window(data.width,data.height,window=data.beginButton,
                         anchor=SE)
    canvas.create_window(data.width/2,data.height,window=data.sentenceButton,
                         anchor=S)
    canvas.create_image(data.width/2,data.height/2-heightMargin/2,anchor=N,
                        image=data.imageIcon)

#Draw pronounce screen
def drawPronounce(canvas,data):
    fontSize = 50
    fontSizePhones = 25
    fontSizeScale = 30
    heightScale = 0.75
    keyScale = 0.25
    xMargin = 5
    yMargin = data.height*0.1
    keyText = "NS = No Stress\nPS = Primary Stress\nSS = Secondary Stress"
    canvas.create_rectangle(0,0,data.width,data.height,fill="cadet blue")
    canvas.create_text(data.width/2,0,text="Learn the Pronounciation",
                       font = "MSerif %d" %(fontSize),anchor=N)
    canvas.create_text(data.width/2,data.height/2,
                       text=data.currentPronounceStress,
                       font = "MSerif %d" %(fontSizePhones),anchor=S)
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)
    canvas.create_window(data.width/2,data.height/2+yMargin,
                         window=data.pronounceHearButton,
                         anchor=N)
    canvas.create_window(data.width/2,data.height*heightScale,anchor=N,
                         window=data.pronounceScale)
    canvas.create_text(data.width/2,data.height*heightScale+100,
                       text="Adjust the scale to change the speed!",
                       anchor=N,font = "MSerif %d" %(fontSizeScale))
    canvas.create_text(xMargin,data.height*keyScale,text=keyText,
                       font = "MSerif %d" %(fontSizePhones),anchor=W)
    
    
    
    
#@TODO properly
#Draw instruction screen
def drawInstruction(canvas,data):    
    fontSize = 50
    textSize = 20
    heightScaleUpper = 0.25
    heightScaleMiddle = 0.65
    heightScaleLower=0.75
    xMargin = data.width/float(80)
    instructionText = "Instructions"
    upperText = "Use the buttons to generate a random word or"
    upperText+="\n         enter your own word in the text box."
    middleText = "Go to the pronounciation page for help with "
    middleText+="articulating the word."
    lowerText = "Lastly press 'Start Recording' to record your own voice "
    lowerText+= "and see how well you did!"
    #actualInstructionText = upperText+"\n"+middleText+"\n"+lowerText
    canvas.create_rectangle(0,0,data.width,data.height,fill="peachpuff")
    canvas.create_text(data.width/2,0,text=instructionText,
                       font="MSerif %d" %(fontSize),anchor=N)
    canvas.create_text(data.width/2,data.height*heightScaleUpper,
                       text=upperText,
                       anchor=S,font = "MSerif %d" %(textSize))
    canvas.create_text(data.width/2,data.height*heightScaleMiddle,
                       text=middleText,
                       anchor=S,font = "MSerif %d" %(textSize))
    canvas.create_text(data.width/2,data.height*heightScaleLower,
                       text=lowerText,
                       anchor=S,font = "MSerif %d" %(textSize))
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)
    canvas.create_image(xMargin,data.height/3,
                        image=data.imageScreenShot0,
                        anchor=NW)
    canvas.create_image(data.width/2+xMargin*15,data.height/3,
                        image=data.imageScreenShot1,
                        anchor=N)

def drawHelper(canvas,data):
    fontSize = 25
    canvas.create_text(data.width/2,0,text=data.helpMessage,
                       font = "MSerif %d" %(fontSize),
                       anchor=N)
#@TODO Split into two
#Draw main screen
def drawBegin(canvas,data):
    drawBeginFirst(canvas,data)
    drawBeginSecond(canvas,data)
    drawHelper(canvas,data)
    
def drawBeginFirst(canvas,data):
    fontSizeInstruct = 40
    fontSizeMainWord = 70
    titleScale = 0.25
    beginText = "Clearly say the word below."
    canvas.create_rectangle(0,0,data.width,data.height,fill="cadet blue")
    canvas.create_text(data.width/2,data.height*titleScale,text=beginText,
                       anchor=N,font="MSerif %d" %(fontSizeInstruct))
    canvas.create_text(data.width/2,data.height/2,text=data.currentWord,
                       anchor=S,font="MSerif %d" %(fontSizeMainWord),
                       fill=data.wordColor)
    canvas.create_window(0,data.height,window=data.instructionButton,
                         anchor=SW)

def drawBeginSecond(canvas,data):
    fontSizeEntry = 20
    heightScale = 0.75
    goHeightShift =100
    yMargin = data.height/float(40)
    canvas.create_window(data.width/2,data.height,window=data.welcomeBackButton
                         ,anchor=S)
    canvas.create_window(data.width,data.height,window=data.randomButton,
                         anchor=SE)
    canvas.create_window(data.width,data.height*heightScale,
                             window=data.recordButton,anchor=NE)
    canvas.create_window(0,data.height*heightScale,
                         window = data.pronounceButton,anchor=NW)
    canvas.create_text(data.width/2,data.height/2+yMargin,
                       text="Entry Box",font="MSerif %d" %(fontSizeEntry),
                       anchor=N)
    canvas.create_window(data.width/2,data.height/2,window=data.entryText,
                         anchor=N)
    canvas.create_window(data.width/2,data.height/2+yMargin*2+goHeightShift,
                         window = data.entryButtonGo)
    
    
def drawSentence(canvas,data):
    drawSentenceFirst(canvas,data)
    drawSentenceSecond(canvas,data)
    drawHelper(canvas,data)
    
def drawSentenceFirst(canvas,data):
    fontSizeEntry = 20
    yMargin = data.height/float(40)
    fontSizePhones = 25
    yMargin = data.height*0.1
    canvas.create_rectangle(0,0,data.width,data.height,fill="cadet blue")
    canvas.create_window(data.width/2,data.height,window=data.welcomeBackButton
                         ,anchor=S)
    canvas.create_text(data.width/2,data.height/2+yMargin,
                       text="Entry Box",font="MSerif %d" %(fontSizeEntry),
                       anchor=N)
    canvas.create_window(data.width/2,data.height/2,window=data.entryTextSent,
                         anchor=N)
    canvas.create_text(data.width/2,data.height/2,
                       text=data.currentSentence,
                       font = "MSerif %d" %(fontSizePhones),anchor=S)

def drawSentenceSecond(canvas,data):
    heightScale = 0.75
    yMargin = data.height/float(40)
    fontSizePhones = 25
    fontSizeScale = 30
    heightScale = 0.75
    keyScale = 0.25
    xMargin = 5
    yMargin = data.height*0.1
    keyText = "NS = No Stress\nPS = Primary Stress\nSS = Secondary Stress"
    canvas.create_text(data.width/2,data.height/2,
                       text=data.currentSentence,
                       font = "MSerif %d" %(fontSizePhones),anchor=S)
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)
    canvas.create_window(data.width/2,data.height/2+yMargin,
                         window=data.hearPronounceSentence,
                         anchor=N)
    
    
#@TODO split into two
#Draw analysis screen
def drawAnalysis(canvas,data):
    initiateAnalysisGraph(data)
    fontSize = 40
    lesserFontSize = 30
    xMargin = data.width/float(10)
    yMargin = data.height/float(20)
    if (data.showTime):
        imageUser = data.imageUserTime
        imageAI = data.imageAITime
    else:
        imageUser = data.imageUserFreq
        imageAI = data.imageAIFreq
        
    canvas.create_rectangle(0,0,data.width,data.height,fill="LavenderBlush3")
    canvas.create_text(data.width/2,0,
                       text="Analysis of your Prounciation is Complete!",
                       font ="MSerif %d" %(fontSize),anchor=N)
    canvas.create_text(data.width/2,3*data.height/4+yMargin,
                       text=data.analysisMessage,
                       font = "MSerif %d" %(lesserFontSize),anchor=S)
    canvas.create_image(xMargin,data.height/2,image=imageAI,
                        anchor=W)
    canvas.create_image(data.width-xMargin,data.height/2,image=imageUser,
                        anchor=E)
    drawAnalysisRest(canvas,data)
    

def drawAnalysisRest(canvas,data):
    xMargin = data.width/float(10)
    yMargin = data.height/float(20)
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)
    canvas.create_window(xMargin,data.height/2-3*yMargin,
                         window=data.analysisAIButton,anchor=SW)
    canvas.create_window(data.width-xMargin,data.height/2-3*yMargin,
                         window=data.analysisUserButton,anchor=SE)
    canvas.create_window(data.width/2,data.height/2-3*yMargin,
                         window=data.graphSwitchButton,anchor=S)
    
#@TODO reduce the length
#initialize data and button
def init(canvas,data):
    data.screen = "welcome"
    data.allWordList = generateWordAndPronounceList()
    fontSize = 30
    toggleFontSize = 10
    entryWidth = 50
    data.wordColor = "black"
    data.recording = False
    data.entryTrigger = False
    data.keepGoing = False
    widthScale = 30
    entryMessage = "Press this button to search for your custom word"
    entryMessage+= " from the entry box."
    instructMessage = "Press this button to go to the instruction page."
    recordMessage = "Press this button to start recording your voice."
    randomMessage = "Press this button to randomize the word on the screen."
    backMessage = "Press this button to go back to the previous page."
    pronounceMessage = "Press this button to go to the pronounciation page."
    data.helpMessageOriginal = "Hover over each widget and look here for help!"
    entryMessage = "Click to enter text here."
    welcomeBackMessage = "Press here to return to the title screen."
    loadImage(data)
    data.currentSentence = ""
    data.scalePronounceBeforeValue = 1.0
    data.showTime = True
    data.helpMessage = data.helpMessageOriginal
    data.instructionButton = Button(canvas,text = "Instructions",
                             font = "MSerif %d" %(fontSize),
                             command = lambda: callInstruction(data),
                             bg="indian red",activebackground="firebrick")
    data.instructionButton.bind("<Enter>",lambda event: changeHelp(data,True,
                                                        instructMessage))
    data.instructionButton.bind("<Leave>",lambda event: changeHelp(data,False,
                                                        ))
    data.beginButton = Button(canvas,text = "Words!",
                              font = "MSerif %d" %(fontSize),
                              command = lambda: callBegin(data),
                              bg="indian red",activebackground="firebrick")
    data.backButton = Button(canvas,text="Back",font = "MSerif %d" %(fontSize),
                             command = lambda: callBack(data),
                             bg="dark slate gray")
    data.welcomeBackButton = Button(canvas,text="Title Screen",
                             font = "MSerif %d" %(fontSize),
                             command = lambda: callWelcomeBack(data),
                             bg="dark slate gray")
    data.sentenceButton = Button(canvas,text="Sentences!",
                                 font= "MSerif %d" %(fontSize),
                                 command = lambda: callSentence(data),
                                 bg="indian red",activebackground="firebrick")
    data.welcomeBackButton.bind("<Enter>",lambda event: changeHelp(data,True,
                                                          welcomeBackMessage))
    data.welcomeBackButton.bind("<Leave>",lambda event: changeHelp(data,False))
    data.backButton.bind("<Enter>",lambda event: changeHelp(data,True,
                                                        backMessage))
    data.backButton.bind("<Leave>",lambda event: changeHelp(data,False,
                                                        ))
    data.randomButton = Button(canvas,text="Randomize",
                               font="MSerif %d" %(fontSize),
                               command=lambda: initiateWordandPronounce(data),
                               bg="steel blue")
    data.randomButton.bind("<Enter>",lambda event: changeHelp(data,True,
                                                        randomMessage))
    data.randomButton.bind("<Leave>",lambda event: changeHelp(data,False,
                                                        ))
    data.recordButton = Button(canvas,text="Start Recording!",
                               font = "MSerif %d" %(fontSize),
                               command = lambda: startRecording(canvas,data),
                               bg = "steel blue")
    data.recordButton.bind("<Enter>",lambda event: changeHelp(data,True,
                                                        recordMessage))
    data.recordButton.bind("<Leave>",lambda event: changeHelp(data,False,
                                                        ))
    data.pronounceButton = Button(canvas,text="Pronounciation",
                                  font = "MSerif %d" %(fontSize),
                                  command = lambda: callPronounce(data),
                                  bg = "steel blue")
    data.pronounceButton.bind("<Enter>",lambda event: changeHelp(data,True,
                                                        pronounceMessage))
    data.pronounceButton.bind("<Leave>",lambda event: changeHelp(data,False))
    data.sentencePronounceButton = Button(canvas,text="Pronounciation",
                                  font = "MSerif %d" %(fontSize),
                                  command = lambda: callSentencePronounce(data)
                                  ,bg = "steel blue")
    data.sentencePronounceButton.bind("<Enter>",lambda event: 
                                    changeHelp(data,True,
                                                        pronounceMessage))
    data.sentencePronounceButton.bind("<Leave>",lambda event: 
                            changeHelp(data,False))
    data.entryButtonGo = Button(canvas,text="Search for word",
                              font = "MSerif %d" %(fontSize),
                              command = lambda: getEntryText(data),
                              bg = "LightSteelBlue3")
    data.entryButtonGo.bind("<Enter>",lambda event: changeHelp(data,True,
                                                              entryMessage))
    data.entryButtonGo.bind("<Leave>",lambda event: changeHelp(data,False))
    data.pronounceHearButton = Button(canvas,
                                      text="Listen to Phonetic Pronounciation",
                                      font = "MSerif %d" %(fontSize),
                                      command = lambda: startPronounce(data),
                                      bg = "steel blue")
    data.pronounceScale = Scale(canvas,from_=0.75,to=1.5,
                         resolution=-1,orient=HORIZONTAL,
                         width=widthScale,length=data.width/2,
                         bg = "royal blue")
    data.pronounceScale.set(1.0)
    data.entryText = Entry(canvas,width=entryWidth)
    data.entryText.configure(highlightbackground="dark blue",
                                 highlightthickness=3)
    data.entryText.bind("<Enter>",lambda event: changeHelp(data,True,
                                                           entryMessage))
    data.entryText.bind("<Leave>",lambda event: changeHelp(data,False))
    data.entryTextSent = Entry(canvas,width=entryWidth)
    data.entryTextSent.configure(highlightbackground="dark blue",
                                 highlightthickness=3)
    data.entryTextSent.bind("<Enter>",lambda event: changeHelp(data,True,
                                                        "Type in a sentence"))
    data.entryText.bind("<Leave>",lambda event: changeHelp(data,False))
    data.analysisAIButton = Button(canvas,text="Artificial Voice",
                                   command = lambda: 
                                       playWav("artificialVoice.wav"),
                                   bg = "PeachPuff3",
                                   font = "MSerif %d" %(fontSize))
    data.analysisUserButton = Button(canvas,text="Your Voice",
                                     command = lambda:
                                         playWav("userVoice.wav"),
                                     font = "MSerif %d" %(fontSize),
                                     bg="PeachPuff3")
    data.graphSwitchButton = Button(canvas,text="Show Frequency Domain",
                                    command = lambda: switchGraphState(data),
                                    font = "MSerif %d" %(toggleFontSize),
                                    bg = "PeachPuff3")
    data.sentenceScale = Scale(canvas,from_=0.75,to=1.5,
                         resolution=-1,orient=HORIZONTAL,
                         width=widthScale,length=data.width/2,
                         bg = "royal blue")
    data.hearPronounceSentence = Button(canvas,
                                      text="Listen to Phonetic Pronounciation",
                                      font = "MSerif %d" %(fontSize),
                                      command = lambda: pronounceSent(data),
                                      bg = "steel blue")

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    pass

#http://www.cs.cmu.edu/~112/notes/events-example0.py
def timerFired(data):
    newValue = float(data.pronounceScale.get())
    #print(getBitRate("fullPhoneticSound.wav"))
    if (data.recording):
        data.counter+=1
        if (data.counter%10==0):
            data.countDown-=1
        if (data.countDown==-1):
            recordAudio(3,"userVoice.wav")
            data.recording = not data.recording
    if (data.screen=="pronounce" and
        not epsilonEqual(data.scalePronounceBeforeValue,newValue,0.1)):
        print("NewValue",newValue)
        print("origingal",data.scalePronounceBeforeValue)
        data.scalePronounceBeforeValue = newValue
       # changeWavFileSpeed("fullPhoneticSound.wav",
        #                   newValue)
       
#http://www.cs.cmu.edu/~112/notes/events-example0.py
def redrawAll(canvas, data):
    if (data.screen == "welcome"):
        drawWelcome(canvas,data)
    elif(data.screen == "instruction"):
        drawInstruction(canvas,data)
    elif(data.screen == "begin"):
        drawBegin(canvas,data)
    elif(data.screen == "analysis"):
        drawAnalysis(canvas,data)
    elif(data.screen == "pronounce"):
        drawPronounce(canvas,data)
    elif(data.screen == "sentences"):
        drawSentence(canvas,data)
    elif (data.screen == "sentencesPronounce"):
        drawSentencePronounce(canvas,data)
        
#Modifed from notes
#http://www.cs.cmu.edu/~112/notes/events-example0.py
def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    init(canvas,data)
    canvas.pack()

    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()
    print("Closed!")
    
def initiateMain():
    width = 1000
    height = 1000
    run(width,height)

    
#-------------------------------Test Functions-------------------------------

#NOTE: Since project requires making graphs and wav files...lot of the tests
#      were conducted in person by listening to each file and looking at graph
#      results.

#Testing peak detection algorithm accuracy of words with AI voice and number
#of vowels...Do not run without slicing the list...dict is simply too big a 
#file to process
def testPeaks():
    fileText = readFile("cmudict.dict")
    wordList = fileText.split("\n")
    counter = 0
    step = 100
    for line in wordList[3::step]:
        spaceIndex = line.find(" ")
        word = line[:spaceIndex]
        pronounciation = line[spaceIndex+1:]
        stringToWav(word,"testingAcc.wav")
        data = getWavData("testingAcc.wav")
        vowelCount = numberOfVowels(pronounciation)
        numberOfPeaks = numOfPeaks(data,5000)
        if (vowelCount - numberOfPeaks)<1:
            counter+=1
    return 100*float(counter)/(float(len(wordList))/step) #Usually around 98%

initiateMain()
