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
from tkinter import *

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
    
#Record input from microphone for given amount of seconds
#Modified from pyaudio documentation website and stackoverflow website
def recordAudio(seconds,fileName,bitRate = 22050*2):    
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

def generateWordAndPronounceList():
    fullString = readFile("cmudict.dict")
    stringList = fullString.split("\n")
    return stringList
def getRandomWordAndPronounce(wordList):
    randomNumber = random.randint(0,len(wordList))
    s = wordList[randomNumber]
    return s
def getWordPronounceTuple(fullString):
    index = fullString.find(" ")
    if (index==-1):
        return None
    wordString = fullString[:index]
    pronounceString = fullString[index+1:]
    return (wordString,pronounceString)


#Event Runner
def init(data):
    pass

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    pass

def timerFired(data):
    pass

def redrawAll(canvas, data):
    pass


def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
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
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(400, 200)
    
#@IGNORE
#personal test code
#data = getWavData("output")
#bitRate = getBitRate("output")
##print(data)
#print("\n")
#
#f = numpy.fft.rfft(data)
#print(f)
#f1 = changeFrequency(f,4000)
#print(f1)
#data = numpy.fft.irfft(f1)
#
##for i in range(len(data)):
#    #x = data[i][0]
#    #y = data[i][1]
#    #data[i][0] = 5
#    #data[i][1] = 5
#data = data.astype(numpy.int32)
##print(data)
#writeWavFile(data,"output2",bitRate)
#playWav("output")
#playWav("output2")



    
