#Roshan Nair
#rsnair
#Term Project - Voice Modulation

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

#Modified from powerpoint
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
    formatPyaudio = pyaudio.paInt32 #3 bytes
    audioInstance = pyaudio.PyAudio()
    stream = audioInstance.open(format = formatPyaudio, channels = numChannels,
                                rate = bitRate, input=True,
                                frames_per_buffer=chunk)
    print("Starting Recording for %d seconds!") %(seconds)    
    frames = []    
    for i in range(0, int(bitRate/chunk*seconds)):
        data = stream.read(chunk) #!?pyaudio encodes data values into string
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
def changeVolume(fileName,multiplier=3):
    data = getWavData(fileName)
    for i in range(len(data)):
        data[i] = data[i]*multiplier
    bitRate = getBitRate(fileName)
    writeWavFile(data,fileName,bitRate)

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
def fourierTransform(wavData):
    #https://www.youtube.com/watch?v=6-llh6WJo1U#t=551.314916
    #Video discusses fourier transformation math link from there as well
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

def inverseFourierTransform(wavData):
    #same formula as above except with positive fundamental frequency...
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
    
#From notes to read files
def readFile(path):
    with open(path, "rt") as f:
        return f.read()
    
#@TODO
#Some bug in wavData transformtaion WORKINPROGRESS
def changeFrequency(wavData,modulationAdder):
    for i in range(len(wavData)):
        wavData[i][0] = wavData[i][0]+modulationAdder
    return wavData

#@TDO remove different pronounce words AKA number in parentheses
def generateWordAndPronounceList():
    fullString = readFile("cmudict.dict")
    stringList = fullString.split("\n")
    return stringList
def getRandomWordAndPronounce(wordList):
    firstWord = "0"
    while (not firstWord.isalpha()):
        randomNumber = random.randint(0,len(wordList))
        s = wordList[randomNumber]
        index = s.find(" ")
        firstWord = s[:index]
    return s
def getWordPronounceTuple(fullString):
    index = fullString.find(" ")
    if (index==-1):
        return None
    wordString = fullString[:index]
    pronounceString = fullString[index+1:]
    return (wordString,pronounceString)



def initiateWordandPronounce(data):
    randomWordandPro = getRandomWordAndPronounce(data.allWordList)
    (data.currentWord,data.currentPronounce)=getWordPronounceTuple(
                                             randomWordandPro)
    stringToWav(data.currentWord,"artificialVoice.wav")

def initiateAnalysisGraph(data):
    imageAI = ImageTk.PhotoImage(file="artificialVoice.png")
    imageUser = ImageTk.PhotoImage(file="userVoice.png")
    data.imageAI = imageAI
    data.imageUser = imageUser
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

#@TODO properly
def drawInstruction(canvas,data):
    fontSize = 60
    instructionText = "@TODO Instructions"
    canvas.create_text(data.width/2,data.height/2,text=instructionText,
                       font="MSerif %d" %(fontSize))
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)

#@TODO Split into two
def drawBegin(canvas,data):
    fontSizeInstruct = 40
    fontSizeMainWord = 70
    heightScale = 0.75
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
#@TODO split into two
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

def drawPronounce(canvas,data):
    fontSize = 30
    canvas.create_text(data.width/2,0,text="Learn the Pronounciation",
                       font = "MSerif %d" %(fontSize),anchor=N)
    canvas.create_text(data.width/2,data.height/2,text=data.currentPronounce,
                       font = "MSerif %d" %(fontSize),anchor=N)
    canvas.create_window(data.width//2,data.height,window=data.backButton,
                         anchor=S)
def callInstruction(data):
    data.originalScreen = data.screen
    data.screen="instruction"

def callBegin(data):
    data.originalScreen = data.screen
    data.screen="begin"    
    initiateWordandPronounce(data)

def callBack(data):
    (data.screen,data.originalScreen) = (data.originalScreen,data.screen)
    
def callPronounce(data):
    data.originalScreen = data.screen
    data.screen = "pronounce"    
    
def callPlayWav():
    playWav("artificialVoice.wav")

#@TODO fix the MVC violation
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

#@TODO reduce the length
def init(canvas,data):
    data.screen = "welcome"
    data.allWordList = generateWordAndPronounceList()
    fontSize = 30
    data.wordColor = "black"
    data.recording = False
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

#image = getImage("artificialVoice.png")








    
