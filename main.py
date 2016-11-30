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
def makeGraph(wavFileName,imgFileName):
    data = getWavData(wavFileName)
    matplotlib.pyplot.clf()
    matplotlib.pyplot.plot(data)
    matplotlib.pyplot.savefig(imgFileName)
    
#Record input from microphone for given amount of seconds
#Modified from pyaudio documentation website and stackoverflow website
def recordAudio(seconds,fileName,bitRate = 22050*2):
    #return
    chunk = 1024 #number of samples in stream
    numChannels = 2 #stereo
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

#Slow down or speed up wave file depending on multiplier >1 or <1
def changeWavFileSpeed(fileName,multiplier):
    data = getWavData(fileName)
    bitRate = getBitRate(fileName)
    writeWavFile(data,fileName,bitRate*multiplier)

#---------------------------Secondary Algorithms/Functions-----------------
    
#From 15-112 notes to read files
def readFile(path):
    with open(path, "rt") as f:
        return f.read()
        
#@TODO
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
                temp+="(Primary Stressed)"
            elif(character=="2"):
                temp+="(Secondary Stressed)"
        else:
            temp+=character
    data.currentPronounce = temp

#@TODO
def writeTextFileArray(fileName,wavFileName):
    numpy.savetxt(fileName,getWavData(wavFileName))

#@TODO
def removeLeadingTrailingZeros(array,fileName="temp.wav"):
    newArray = []
    for element in array:
        if (element!=0):
            newArray.append(element)           
    newNumpyArray = numpy.asarray(newArray)
    writeWavFile(newNumpyArray,fileName)            

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

#Initialize the graphs for both AI voice and user voice
def initiateAnalysisGraph(data):
    imageAI = ImageTk.PhotoImage(file="artificialVoice.png")
    imageUser = ImageTk.PhotoImage(file="userVoice.png")
    data.imageAI = imageAI
    data.imageUser = imageUser

#Get word only without pronounciation
def getWordOnly(string):
    firstSpaceIndex = string.find(" ")
    return string[:firstSpaceIndex]

#Since cmuDict is sorted by alphabet, can find quicker
def searchForWord(data):
    data.onlyWordList = list(map(getWordOnly,data.allWordList))
    index = data.onlyWordList.index(data.entryString)
    return index
        
    #binarySearchForWord(data,onlyWordList)    
    
#@TODO Binary sort through to find text
def getEntryText(data):
    data.entryString = data.entryText.get()
    if (len(data.entryString.strip())==0):
        return
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

#Button call to main screen
def callBegin(data):
    data.originalScreen = data.screen
    data.screen="begin"    
    initiateWordandPronounce(data)

#Button call for back
def callBack(data):
    (data.screen,data.originalScreen) = (data.originalScreen,data.screen)

#Button call for pronounce screen
def callPronounce(data):
    data.originalScreen = data.screen
    data.screen = "pronounce"
    
#Button call to play Sound
def callPlayWav():
    playWav("artificialVoice.wav")

#@TODO fix the MVC violation
#Button call to start recording
def startRecording(canvas,data):
    data.originalScreen = data.screen
    data.recordButton.configure(bg="red")
    canvas.delete(ALL)
    redrawAll(canvas, data)
    canvas.update()
    data.recordButton.configure(bg="grey")
    recordAudio(3,"userVoice.wav")
    data.screen = "analysis"
    makeGraph("artificialVoice.wav","artificialVoice.png")
    makeGraph("userVoice.wav","userVoice.png")

#-------------------------------GUI Instructions------------------

#Draw splash screen
def drawWelcome(canvas,data):
    fontSize = 60
    canvas.create_rectangle(0,0,data.width,data.height,fill="white")
    canvas.create_text(data.width//2,data.height//2,
                       text = "Welcome to *insert Title",
                       font="MSerif %d" %(fontSize),
                       anchor = S)
    canvas.create_window(0,data.height,window=data.instructionButton,anchor=SW)
    canvas.create_window(data.width,data.height,window=data.beginButton,
                         anchor=SE)

#Draw pronounce screen
def drawPronounce(canvas,data):
    fontSize = 20
    canvas.create_text(data.width/2,0,text="Learn the Pronounciation",
                       font = "MSerif %d" %(fontSize),anchor=N)
    canvas.create_text(data.width/2,data.height/2,text=data.currentPronounce,
                       font = "MSerif %d" %(fontSize),anchor=N)
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)

#@TODO properly
#Draw instruction screen
def drawInstruction(canvas,data):
    fontSize = 60
    instructionText = "@TODO Instructions"
    canvas.create_text(data.width/2,data.height/2,text=instructionText,
                       font="MSerif %d" %(fontSize))
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)

#@TODO Split into two
#Draw main screen
def drawBegin(canvas,data):
    fontSizeInstruct = 40
    fontSizeMainWord = 70
    heightScale = 0.75
    goHeightShift =100
    beginText = "Clearly say the word below."
    canvas.create_text(data.width/2,0,text=beginText,
                       anchor=N,font="MSerif %d" %(fontSizeInstruct))
    canvas.create_text(data.width/2,data.height/2,text=data.currentWord,
                       anchor=S,font="MSerif %d" %(fontSizeMainWord),
                       fill=data.wordColor)
    canvas.create_window(0,data.height,window=data.instructionButton,
                         anchor=SW)
    canvas.create_window(data.width/2,data.height,window=data.backButton,
                         anchor=S)
    canvas.create_window(data.width,data.height,window=data.randomButton,
                         anchor=SE)
    canvas.create_window(data.width/2,data.height*heightScale,
                             window=data.recordButton,anchor=N)
    canvas.create_window(data.width,data.height*heightScale,
                         window = data.listenWordButton,anchor=NE)
    canvas.create_window(0,data.height*heightScale,
                         window = data.pronounceButton,anchor=NW)
    canvas.create_window(data.width/2,data.height/2,window=data.entryText,
                         anchor=N)
    canvas.create_window(data.width/2,data.height/2+goHeightShift,
                         window = data.entryButtonGo)
    
#@TODO split into two
#Draw analysis screen
def drawAnalysis(canvas,data):
    initiateAnalysisGraph(data)
    fontSize = 60
    xScale = 50
    yScale = 3
    xMargin = data.width/xScale
    yMargin = data.height/yScale
    canvas.create_text(data.width/2,0,text="Analysis",
                       font ="MSerif %d" %(fontSize),anchor=N)
    canvas.create_text(0,yMargin,text="AI Voice",
                       font ="MSerif %d" %(fontSize),anchor=SW)
    canvas.create_text(data.width,yMargin,text="Your Voice",
                       font ="MSerif %d" %(fontSize),anchor=SE)
    canvas.create_image(xMargin,data.height/2,image=data.imageAI,
                        anchor=W)
    canvas.create_image(data.width-xMargin,data.height/2,image=data.imageUser,
                        anchor=E)
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)

#@TODO reduce the length
#initialize data and button
def init(canvas,data):
    data.screen = "welcome"
    data.allWordList = generateWordAndPronounceList()
    fontSize = 30
    entryWidth = 50
    data.wordColor = "black"
    data.recording = False
    data.entryTrigger = False
    data.instructionButton = Button(canvas,text = "Instructions",
                             font = "MSerif %d" %(fontSize),
                             command = lambda: callInstruction(data))
    data.beginButton = Button(canvas,text = "Begin!",
                              font = "MSerif %d" %(fontSize),
                              command = lambda: callBegin(data))
    data.backButton = Button(canvas,text="Back",font = "MSerif %d" %(fontSize),
                             command = lambda: callBack(data))
    data.randomButton = Button(canvas,text="Randomize Word",
                               font="MSerif %d" %(fontSize),
                               command=lambda: initiateWordandPronounce(data))
    data.recordButton = Button(canvas,text="Start Recording!",
                               font = "MSerif %d" %(fontSize),
                               command = lambda: startRecording(canvas,data))
    data.listenWordButton = Button(canvas,text="Listen to word",
                                   font = "MSerif %d" %(fontSize),
                                   command = lambda: callPlayWav())
    data.pronounceButton = Button(canvas,text="Pronounciation",
                                  font = "MSerif %d" %(fontSize),
                                  command = lambda: callPronounce(data))
    data.entryButtonGo = Button(canvas,text="Enter",
                              font = "MSerif %d" %(fontSize),
                              command = lambda: getEntryText(data))
    data.entryText = Entry(canvas,width=entryWidth)

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    pass

def timerFired(data):
    if (data.recording):
        data.counter+=1
        if (data.counter%10==0):
            data.countDown-=1
        if (data.countDown==-1):
            recordAudio(3,"userVoice.wav")
            data.recording = not data.recording

def redrawAll(canvas, data):
    if (data.screen == "welcome"):
        drawWelcome(canvas,data)
    elif(data.screen == "instruction"):
        drawInstruction(canvas,data)
    elif(data.screen == "begin"):
        drawBegin(canvas,data)
        drawEntryTrigger(canvas,data)
    elif(data.screen == "analysis"):
        drawAnalysis(canvas,data)
    elif(data.screen == "pronounce"):
        drawPronounce(canvas,data)
        

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

initiateMain()


#@IGNORE currently testing TODO functions

#data = getWavData("artificialVoice.wav")
#data = data[:29422/4]
#writeWavFile(data,"artificialVoice2.wav")
#writeTextFileArray("artificialVoice2.txt","artificialVoice2.wav")
#removeLeadingTrailingZeros(data,"artificialVoice3.wav")
#makeGraph("artificialVoice3.wav","artificialVoice3.png")
#data = data[]








    
