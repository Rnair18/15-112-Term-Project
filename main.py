import numpy
import scipy
import math
import winsound
import pyaudio
import wave

from scipy.io.wavfile import read
from scipy.io.wavfile import write

from comtypes.gen import SpeechLib

from comtypes.client import CreateObject

#Modified from Stackoverflow source
def stringToWav(s,fileName):
    #Default bit rate is 22050
    fileName = fileName+".wav"
    engine = CreateObject("SAPI.SpVoice")
    stream = CreateObject("SAPI.SpFileStream")
    stream.Open(fileName, SpeechLib.SSFMCreateForWrite)
    engine.AudioOutputStream = stream
    engine.speak(s)
    stream.Close()

#Modified from powerpoint
def getWavData(fileName):
    fileName+=".wav"
    data = scipy.io.wavfile.read(fileName)
    return data[1]
def writeWavFile(wavData,fileName,bitrate = 22050):
    fileName+=".wav"
    scipy.io.wavfile.write(fileName,bitrate,wavData)  

    
def playWav(fileName):
    fileName = fileName+".wav"
    winsound.PlaySound(fileName,winsound.SND_FILENAME)
def increaseVolume(fileName,multiplier=3):
    data = getWavData(fileName)
    for i in range(len(data)):
        data[i] = data[i]*multiplier
    writeWavFile(data,fileName)
    
class ComplexNumber(object):    
    def __init__(self,real,imaginary):
        self.real = real
        self.imaginary = imaginary
    def __repr__(self):
        if (self.imaginary<0):
            return "%f-%fj" %(float(self.real),float(self.imaginary))
        elif(self.imaginary>0):
            return "%f+%fj" %(float(self.real),float(self.imaginary))
        else:
            return "%f" %(float(self.real))       
    def add(self,other):
        if(isinstance(other,ComplexNumber)):
            newReal = self.real+other.real
            newImaginary = self.imaginary+other.imaginary
            newComplexNum = ComplexNumber(newReal,newImaginary)
            return newComplexNum
        elif(isinstance(other,int) or isinstance(other,float)):
            newReal = self.real+other
            newImaginary = self.imaginary
            newComplexNum = ComplexNumber(newReal, newImaginary)
        else:
            return None
    def multiply(self,other):
        if (isinstance(other,ComplexNumber)):
            newReal = self.real*other.real-self.imaginary*other.imaginary
            newImaginary = self.real*other.imaginary+self.imaginary*other.real
            newComplexNum = ComplexNumber(newReal,newImaginary)
            return newComplexNum
        elif(isinstance(other,int) or isinstance(other,float)):
            newReal = self.real*other
            newImaginary = self.imaginary*other
            newComplexNum = ComplexNumber(newReal,newImaginary)
            return newComplexNum
        else:
            return None
    def getMagnitude(self):
        result = math.sqrt(self.real**2+self.imaginary**2)
        return result
    def getCopy(self):
        newComplexNum = ComplexNumber(self.real,self.imaginary)
        return newComplexNum  

def recordAudio(seconds,fileName,bitRate = 22050*2):
    #modified from pyaudio documentation website
    chunk = 1024 #number of samples in stream
    fileName = fileName+".wav"
    numChannels = 2 #stereo
    formatPyaudio = pyaudio.paInt32 #3bytes
    audioInstance = pyaudio.PyAudio()
    stream = audioInstance.open(format = formatPyaudio, channels = numChannels,
                                rate = bitRate, input=True,
                                frames_per_buffer=chunk)
    print("Starting Recording for %d seconds!") %(seconds)
    
    frames = []
    
    for i in range(0, int(bitRate/chunk*seconds)):
        data = stream.read(chunk)
        frames.append(data)
        #each data is a wierd string value
    print("Finished Recording!")
    stream.stop_stream()
    stream.close()
    audioInstance.terminate()
    
    #Using wave module creates wav file
    waveFile = wave.open(fileName, 'wb')
    waveFile.setnchannels(numChannels)
    waveFile.setsampwidth(audioInstance.get_sample_size(formatPyaudio))
    waveFile.setframerate(bitRate)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def addBoth(transform,wavData):
    newList = []
    for i in range(len(transform)):
        summer = 0
        for dataIndex in range(len(wavData)):
            summer+=transform[i][dataIndex]*wavData[dataIndex]
        newList.append(summer)
    return newList
            

def fourierTransform(wavData):
    #https://www.youtube.com/watch?v=6-llh6WJo1U#t=551.314916
    #link from there as well
    fundamentalFrequency = -2*math.pi
    dimension = wavData.shape
    rowLength = dimension[0]
    if (rowLength>30):
        return None
    wavData = numpy.asarray(wavData, dtype=float) #Convert wave data into
                                                  #numpy array
    
    newList = numpy.arange(rowLength)
    k = newList.reshape((rowLength, 1))
    transform = numpy.exp(fundamentalFrequency * k * newList/ rowLength)
    return numpy.asarray(addBoth(transform,wavData))
    
#data = getWavData("testing4") #lenght is 51910
#data = data[1][10000:10010]
#print(data)
#print(fft.rfft(data))
#print(fourierTransform(data))
print("Testing")
#recordAudio(5,"output")
data = getWavData("testing4")
print(fourierTransform(data))

#

#

    

    