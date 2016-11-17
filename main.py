from numpy import *
import scipy
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import math
import winsound
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
    return (data[0],data[1])
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
    
def builtInFFT(wavData):
    data = fft.rfft(wavData)
    return data
    
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
        if(isinstance(other,Complex)):
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
        if (isinstance(other,Complex)):
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

def fastFourierTransform(wavData):
    #https://www.youtube.com/watch?v=6-llh6WJo1U#t=551.314916
    fundamentalFrequency = 2*math.pi
    
    print(fundamentalFrequency)

def test():
    stringToWav("Denzel and Mihir sitting in a tree, K I S S I N G","weird")
    playWav("weird")
    

test()

    

    