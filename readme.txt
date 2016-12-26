The application, SpeakIt! helps people with understanding and articulating english words and sentences. 
It can phonetically sound out words as well as record user audio...and inform them on improvements they can make in their pronounciation. For words and their pronounciations I used files provided by Carnegie Mellon University Pronouncing Dictionary.

I used the anaconda python environment which has a lot of built in modules...while others are easy to download via command prompt.
You can still download the modules separately however.
The project uses the following modules:

numpy, scipy - http://www.scipy.org/scipylib/download.html
pyaudio - https://people.csail.mit.edu/hubert/pyaudio/#downloads
matplotlib - http://matplotlib.org/users/installing.html
speech_recognition - https://pypi.python.org/pypi/SpeechRecognition/
comtypes.gen, comtypes.client - https://people.csail.mit.edu/hubert/pyaudio/#downloads (windows only)

Python 2.7 is required to run the code. Simply run main.py to start the application.
**key note however: Project reads and writes numerous wav files and png files so allocate a separate folder before running.