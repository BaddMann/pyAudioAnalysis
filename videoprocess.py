#!/usr/bin/env python2.7
import argparse
import os
import audioop
import numpy
import glob
import scipy
import subprocess
import wave
import cPickle
import threading
import shutil
import ntpath
import matplotlib.pyplot as plt
import audioFeatureExtraction as aF
import audioTrainTest as aT
import audioSegmentation as aS
import audioVisualization as aV
import audioBasicIO
import utilities as uT
import scipy.io.wavfile as wavfile
import matplotlib.patches
from moviepy.editor import *



def silenceRemovalWrapper(inputFile, smoothingWindow, weight):
    print "AudioFile in Silence Function " + str(inputFile)
    if not os.path.isfile(inputFile):
        raise Exception("Input audio file not found!")

    [Fs, x] = audioBasicIO.readAudioFile(inputFile)                                        # read audio signal
    segmentLimits = aS.silenceRemoval(x, Fs, 0.05, 0.05, smoothingWindow, weight, False)    # get onsets
    for i, s in enumerate(segmentLimits):
        print str(i) + " Clip: " + str(s)
        duration = s[1] - s[0]
        print "Duration: " + str(duration)
        if duration > 20:
            startsecs = str("{0:5.3f}".format(s[0])).zfill(9)
            endsecs = str("{0:5.3f}".format(s[1])).zfill(9)
            strOut = "{0:s}_{1:s}-{2:s}.wav".format(inputFile[0:-4], startsecs, endsecs)
            #wavfile.write(strOut, Fs, x[int(Fs * s[0]):int(Fs * s[1])])
            videoresult = VideoFileClip("{0:s}.mp4".format(inputFile[0:-4])).subclip(s[0],s[1])
            videoresult.write_videofile(("{0:s}_{1:s}-{2:s}.mp4".format(inputFile[0:-4], startsecs, endsecs)), 
					                               write_logfile=False, 
					                               codec='libx264', 
					                               audio_codec='aac',
                                                   temp_audiofile=("{0:s}_{1:s}-{2:s}.m4a".format(inputFile[0:-4], startsecs, endsecs)), 
					                               preset="ultrafast", 
					                               remove_temp=True )
def parse_arguments():
    parser = argparse.ArgumentParser(description="A demonstration script for pyAudioAnalysis library")
    tasks = parser.add_subparsers(
        title="subcommands", description="available tasks", dest="task", metavar="")

    Mp4toWav = tasks.add_parser("Mp4toWav", help="Convert .mp4 file to .wav format")
    Mp4toWav.add_argument("-i", "--input", required=True, help="Input folder")
    Mp4toWav.add_argument("-r", "--rate", type=int, choices=[8000, 16000, 32000, 44100],
                           required=True, help="Samplerate of generated WAV files")
    Mp4toWav.add_argument("-c", "--channels", type=int, choices=[1, 2],
                           required=True, help="Audio channels of generated WAV files")

    silrem = tasks.add_parser("silenceRemoval", help="Remove silence segments from a recording")
    silrem.add_argument("-i", "--input", required=True, help="input audio file")
    silrem.add_argument("-s", "--smoothing", type=float, default=1.0, help="smoothing window size in seconds.")
    silrem.add_argument("-w", "--weight", type=float, default=0.5, help="weight factor in (0, 1)")

    bothSteps = tasks.add_parser("bothSteps", help="Remove silence segments from a recording")
    bothSteps.add_argument("-i", "--input", required=True, help="input audio file")
    bothSteps.add_argument("-s", "--smoothing", type=float, default=3.0, help="smoothing window size in seconds.")
    bothSteps.add_argument("-w", "--weight", type=float, default=0.05, help="weight factor in (0, 1)")
    bothSteps.add_argument("-r", "--rate", type=int, choices=[8000, 16000, 32000, 44100],
                           required=True, help="Samplerate of generated WAV files")
    bothSteps.add_argument("-c", "--channels", type=int, choices=[1, 2],
                           required=True, help="Audio channels of generated WAV files")

    return parser.parse_args()

def Mp4WavWrapper(vidinput, samplerate, channels):
    audiofilter = '-af \"compand=.3|.3:1|1:-90/-60|-60/-40|-40/-30|-20/-20:6:0:-90:0.2\"'
    ffmpegString = 'ffmpeg -i ' + '\"' + vidinput + '\" ' + audiofilter + ' -vn -ar ' + str(samplerate) + ' -ac ' + str(channels) + ' ' + '\"' + os.path.splitext(vidinput)[0] + '\"' + '.wav' 
    os.system(ffmpegString)

def bothStepsWrapper(vidinput, samplerate=8000, channels=1, smoothingWindow=float(3.0), weight=float(0.05)):
    Mp4WavWrapper(vidinput, samplerate, channels)
    audiofile='\"' + os.path.splitext(vidinput)[0]  + '.wav' + '\"'
    print "AudioFile: " + str(audiofile)
    silenceRemovalWrapper(audiofile, smoothingWindow, weight)



##### not done


##python audioAnalysis.py silenceRemoval -i C:\Users\glencroftplay\test.wav --smoothing 3.0 --weight 0.05

##ffmpeg -i Z:\2017-01-23-VarietyShow.mp4 -af "compand=.3|.3:1|1:-90/-60|-60/-40|-40/-30|-20/-20:6:0:-90:0.2" -vn -ac 1 -ar 8000 Z:\2017-01-23-VarietyShow.wav


if __name__ == "__main__":
    args = parse_arguments()

    if args.task == "Mp4toWav":                                                            # Convert to wav (batch - file)
        Mp4WavWrapper(args.input, args.rate, args.channels)
    elif args.task == "silenceRemoval":                                                       # Detect non-silent segments in a WAV file and output to seperate WAV files
        silenceRemovalWrapper(args.input, args.smoothing, args.weight)
    elif args.task == "bothSteps":                                                       # Perform both Previous steps in sequence
        bothStepsWrapper(args.input, args.rate, args.channels, args.smoothing, args.weight)