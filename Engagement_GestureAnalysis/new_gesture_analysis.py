import time, threading
from threading import Timer
import thread
import OSC
from array import *
import numpy
import sys
import os
#import pylab
import random
import string
from numpy import isnan
from math import isnan, isinf
#from cgkit.cgtypes import *
from datetime import datetime

import matplotlib.pyplot as plt
plt.rcParams['backend'] = 'TkAgg'

from scipy.signal import lfilter

from dataCollectors import *
from gestureProcessing import *
from classes import *
#import cluster

#import globRehearsal
#import activita
#rehearsal = globRehearsal.getState()


automation = 1
eng = 0
activity = 0
totalAcc = 0

# Gesture clusters
#clusters = [0, cluster.cluster(), cluster.cluster(), cluster.cluster()]
gestureList = []

# OSC clients
clients = [0, OSC.OSCClient(), OSC.OSCClient(), OSC.OSCClient()]
clients[1].connect( ('10.0.0.1', 9000) ) # note that the argument is a tupple and not two arguments
clients[2].connect( ('10.0.0.2', 9000) ) # note that the argument is a tupple and not two arguments
clients[3].connect( ('10.0.0.3', 9000) ) # note that the argument is a tupple and not two arguments

# OSC server IP and port
receive_address = '10.0.0.4', 9000

s = OSC.ThreadingOSCServer(receive_address) # basic
s.addDefaultHandlers()

manualControl = OSC.OSCMessage()
automaticControl = OSC.OSCMessage()
manualControl.setAddress("/manual")
automaticControl.setAddress("/manual")
manualControl.append(1)
automaticControl.append(0)


def bodyOrientation_handler(addr, tags, stuff, source):
    msgSize = numpy.size(stuff)
    for i in xrange(msgSize):
        try:
            if (stuff[i] == "lean"):
                bodyOrientation.leanX = stuff[i+1]
                bodyOrientation.leanY = stuff[i+2]
            if (stuff[i] == "neckOrientation"):
                bodyOrientation.headPitch = stuff[i+1]
                bodyOrientation.headYaw = stuff[i+2]
                bodyOrientation.headRoll = stuff[i+3]
        except:
            pass


def faceOrientation_handler(addr, tags, stuff, source):
    faceOrientation.pointOfInterest = stuff[0]
    faceOrientation.instrument_1 = stuff[1]
    faceOrientation.instrument_2 = stuff[2]
    faceOrientation.instrument_3 = stuff[3]
    faceOrientation.audience = stuff[4]

def faceValue_handler(addr, tags, stuff, source):
    msgSize = numpy.size(stuff)
    for i in xrange(msgSize):
        try:
            if (stuff[i] == "jawOpen"):
                facialFeature.jawOpen = stuff[i+1]
            #    if (stuff[i+1] > jawOpenThreshold):
            #        facialFeaturesProc.jawOpen = 1
            #    else:
            #        facialFeaturesProc.jawOpen = 0

            if (stuff[i] == "jawSlideRight"):
                facialFeature.jawSlideRight = stuff[i+1]
            if (stuff[i] == "leftEyeClosed"):
                facialFeature.leftEyeClosed = stuff[i+1]
            if (stuff[i] == "rightEyeClosed"):
                facialFeature.rightEyeClosed = stuff[i+1]
            if (stuff[i] == "leftCheekPuff"):
                facialFeature.leftCheekPuff = stuff[i+1]
            if (stuff[i] == "rightCheekPuff"):
                facialFeature.rightCheekPuff = stuff[i+1]
            if (stuff[i] == "leftEyebrowLowerer"):
                facialFeature.leftEyebrowLowerer = stuff[i+1]
            if (stuff[i] == "rightEyebrowLowerer"):
                facialFeature.rightEyebrowLowerer = stuff[i+1]
            if (stuff[i] == "lipCornerDepressorLeft"):
                facialFeature.lipCornerDepressorLeft = stuff[i+1]
            if (stuff[i] == "lipCornerDepressorRight"):
                facialFeature.lipCornerDepressorRight = stuff[i+1]
            if (stuff[i] == "lipCornerPullerLeft"):
                facialFeature.lipCornerPullerLeft = stuff[i+1]
            if (stuff[i] == "lipCornerPullerRight"):
                facialFeature.lipCornerPullerRight = stuff[i+1]
            if (stuff[i] == "lipPucker"):
                facialFeature.lipPucker = stuff[i+1]
            if (stuff[i] == "lipStretcherLeft"):
                facialFeature.lipStretcherLeft = stuff[i+1]
            if (stuff[i] == "lipStretcherRight"):
                facialFeature.lipStretcherRight = stuff[i+1]
            if (stuff[i] == "lowerLipDepressorLeft"):
                facialFeature.lowerLipDepressorLeft = stuff[i+1]
            if (stuff[i] == "lowerLipDepressorRight"):
                facialFeature.lowerLipDepressorRight = stuff[i+1]
        except:
            pass


def faceTrackState_handler(addr, tags, stuff, source):
    #print stuff
    state = stuff[0]
    #print "Face: " + str(state)
    if (faceTracker.state == 0 and state == 1):
        faceTracker.state = state
        #print "Face found: " + str(state)
        faceStateCollector(state)


    if (faceTracker.state == 1 and state == 0):
        faceTracker.state = state
        #print "Face lost: " + str(state)
        faceStateCollector(state)

def jointXYZ_handler(addr, tags, stuff, source):
    msgSize = numpy.size(stuff)
    totalAcc = 0
    #print str(msgSize)
    for i in xrange(msgSize):
        try:
            if (stuff[i] == "handTipLeft"):
                acc = handTipLeft.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc
                #print str(acc)

            if (stuff[i] == "handTipRight"):
                acc = handTipRight.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                #print "handTipRight " + str(handTipRight.x)
                totalAcc = totalAcc + acc

            if (stuff[i] == "wristLeft"):
                acc = wristLeft.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc
                           
            if (stuff[i] == "wristRight"):
                acc = wristRight.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc
                #print str(acc)


            if (stuff[i] == "handLeft"):
                acc = handLeft.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                #print "L: " + str(round(handLeft.acc,3))
                totalAcc = totalAcc + handLeft.acc
                

            if (stuff[i] == "handRight"):
                acc = handRight.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                #print "R: " + str(round(handRight.acc,0))
                totalAcc = totalAcc + handRight.acc

            if (stuff[i] == "elbowLeft"):
                acc = elbowLeft.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + elbowLeft.acc

            if (stuff[i] == "elbowRight"):
                acc = elbowRight.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + elbowRight.acc

            if (stuff[i] == "shoulderLeft"):
                acc = shoulderLeft.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + shoulderLeft.acc
            
            if (stuff[i] == "shoulderRight"):
                acc = shoulderRight.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + shoulderRight.acc

            if (stuff[i] == "head"):
                acc = head.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                #print "Acc: " + str(round(acc,3))
                totalAcc = totalAcc + head.acc    
                        
            if (stuff[i] == "spineShoulder"):
                acc = spineShoulder.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc

            if (stuff[i] == "neck"):
                acc = neck.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + neck.acc

            #if (stuff[i] == "spineBase"):
            #    acc = spineBase.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
            #    totalAcc = totalAcc + acc

            if (stuff[i] == "spineMid"):
                acc = spineMid.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                #print "spine mix x : " + str(spineMid.x)
                totalAcc = totalAcc + acc
        except:
            pass
    
    totalAccCollector(totalAcc)


def controlInput_handler(addr, tags, stuff, source):
    pass

def handProximity_handler(addr, tags, stuff, source):
    msgSize = numpy.size(stuff)
    #print stuff

    for i in xrange(msgSize):

        if (stuff[i] == "handRight"):

            instrument = stuff[i+1]

            if instrument != "far":
                instrument = instrument[-1]
                instrument = string.atoi(instrument)
      
                if (handRight.proximity != instrument):

                    #print "right instrument " + str(instrument)
                    handRight.proximity = instrument
                    clients[instrument].send(manualControl)
                    handProximityCollector("right", str(instrument))

                    for n in range(1,4):
                        if (handLeft.proximity != n and instrument != n):
                            #print "n = " + str(n) + " instrument = " + str(instrument) + " n-1: " + str(n-1)
                            #print "close right automatic : " + str(n)
                            clients[n].send(automaticControl)
                         
            if (instrument == "far"):
                if (handRight.proximity != 0):
                    handRight.proximity = 0
                    handProximityCollector("right", "far")
                    #print "right far"

                    for n in range(1, 4):
                        if (handLeft.proximity != n):
                            #print "far right automatic : " + str(n)
                            clients[n].send(automaticControl)

        if (stuff[i] == "handLeft"):

            instrument = stuff[i+1]

            if instrument != "far":
                instrument = instrument[-1]
                instrument = string.atoi(instrument)
      
                if (handLeft.proximity != instrument):

                    #print "left instrument " + str(instrument)
                    handLeft.proximity = instrument
                    clients[instrument].send(manualControl)
                    handProximityCollector("left", str(instrument))

                    for n in range(1,4):
                        if (handRight.proximity != n and instrument != n):
                            #print "n = " + str(n) + " instrument = " + str(instrument) + " n-1: " + str(n-1)
                            #print "close right automatic : " + str(n)
                            clients[n].send(automaticControl)
                         
            if (instrument == "far"):
                if (handLeft.proximity != 0):
                    handLeft.proximity = 0
                    handProximityCollector("left", "far")
                    #print "left far"

                    for n in range(1, 4):
                        if (handRight.proximity != n):
                            #print "far left automatic : " + str(n)
                            clients[n].send(automaticControl)


# Previous move

def process_input(instrument, hand, value):

    if hand == "left":       
        if agents[instrument].manual == 1:
            if agents[instrument].device_state == 0 and value > 30:
                print "INSTRUMENT: " + str(instrument) + " ON"
                agents[instrument].device_state = 1
            agents[instrument].current_L = value
            agents[instrument].values_L = numpy.insert(agents[instrument].values_L, 0, value) # add first
            agents[instrument].prevMove = "user"
            
    if hand == "right":       
        if agents[instrument].manual == 1:
            if agents[instrument].device_state == 0 and value > 30:
                print "INSTRUMENT: " + str(instrument) + " ON"
                agents[instrument].device_state = 1
            agents[instrument].current_R = value
            agents[instrument].values_R = numpy.insert(agents[instrument].values_R, 0, value) # add first
            agents[instrument].prevMove = "user"


    if agents[instrument].current_L < 30 and agents[instrument].current_R < 30 and agents[instrument].manual == 1:
            if agents[instrument].device_state == 1:
                print "INSTRUMENT: " + str(instrument) + " OFF"
                agents[instrument].device_state = 0

prev_energy = 0
tempo = 100



def process_features(instrument, feature, value):
    #print "process feature: " + str(feature) + " value: " + str(value) + " instrument: " + str(instrument)
    global prev_energy, tempo
    # These are recorded for gestures
    if agents[instrument].manual == 1:

        if feature == "centroid":
            if isnan(value) == 0 and value != 0:
                #print "centroid: " + str(value)
                agents[instrument].centroid = numpy.insert(agents[instrument].centroid, 0, value)

        if feature == "smoothness":
            if value != 0:
                #print "smoothness: " + str(value)
                agents[instrument].smoothness = numpy.insert(agents[instrument].smoothness, 0, value)

        if feature == "energy":
            if isnan(value) == 0 and value != 0:
                agents[instrument].energy = numpy.insert(agents[instrument].energy, 0, value)
        
        #if feature == "myodyn":
        #    agents[instrument].myodyn = numpy.insert(agents[instrument].myodyn, 0, value)

    # These are stored for musical scene analysis
    if feature == "smoothness":
        if value != 0:
            agents[instrument].smoothness_mus = numpy.insert(agents[instrument].smoothness_mus, 0, value)
    if feature == "centroid":
        if isnan(value) == 0 and value != 0:
            agents[instrument].centroid_mus = numpy.insert(agents[instrument].centroid_mus, 0, value)
    if feature == "energy":
        if isnan(value) == 0 and value > 0:
            agents[instrument].energy_mus = numpy.insert(agents[instrument].energy_mus, 0, value)

   # These are to trigger gesture playback

   #print value
    if agents[instrument].prevMove == "user": # or agents[instrument].prevMove == "CPU":
        if feature == "energy":
            #print "energia: " + str(value)
            # Jos arvo on 0, katso mika oli edellinen arvo
            if value < 40:
                if agents[instrument].prev_energy == "on":
                    agents[instrument].prev_energy = "off"

                    #print "New Energy ZERO detected"
                    #pass
                    gesturePlayback(tempo)


            if value > 52:
                if agents[instrument].prev_energy == "off":
                    agents[instrument].prev_energy = "on"
                                     
        #print value
        if feature == "attack3": #

            if value == 1:
                try:
                    print "attack3 + THIRD: "  + str(engagement.third[-1])
                    eng_state = engagement.third[-1]
                    if engagement.third[-1] == "mid":# or eng_state == "high" or eng_state == "low":
                        #print "attack playback"
                        #pass
                        gesturePlayback(tempo)
                except:
                    pass

        if feature == "attack6": #
            if value == 1:
                try:
                    print "attack6 + third: "  + str(engagement.third[-1])
                    eng_state = engagement.third[-1]
                    if engagement.third[-1] == "high":# or eng_state == "high" or eng_state == "low":
                        gesturePlayback(tempo)
                except:
                    pass            
                

        if feature == "tempo":
            #print "tempo: "  + str(tempo)
            tempo = value


     
def agent_handler(addr, tags, stuff, source):
    #print "OSC list: " + str(stuff)
    global gestureList
    #print "addr: " + str(addr)
    instrument = addr[-1]
    instrument = string.atoi(instrument)
    #value = stuff[1]

    size = numpy.size(stuff)

    for i in xrange(size):
        if stuff[i] == "left":
            #print "LEFT: " + str(stuff[i+1])
            process_input(instrument, "left", stuff[i+1])
        if stuff[i] == "right":
            #print "RIGHT: " + str(stuff[i+1])
            process_input(instrument, "right", stuff[i+1])


        if stuff[i] == "smoothness":
            process_features(instrument, "smoothness", stuff[i+1]) 
        if stuff[i] == "irregularity":
            process_features(instrument, "irregularity", stuff[i+1])
        if stuff[i] == "flatness":
            process_features(instrument, "flatness", stuff[i+1])
        if stuff[i] == "centroid":
            #print "centroid: " + str(stuff[i+1])
            process_features(instrument, "centroid", stuff[i+1])
        if stuff[i] == "energy":
            process_features(instrument, "energy", stuff[i+1])
        if stuff[i] == "attack3":
            process_features(instrument, "attack3", stuff[i+1])
        if stuff[i] == "attack6":
            process_features(instrument, "attack6", stuff[i+1])
        if stuff[i] == "tempo":
            process_features(instrument, "tempo", stuff[i+1])

        if stuff[i] == "myodyn":
            process_features(instrument, "myodyn", stuff[i+1])

        if stuff[i] == "manual":
            if agents[instrument].manual == 1 and stuff[i+1] == 0:
                agents[instrument].manual = 0

                if numpy.size(agents[instrument].values_L) > 10:
                    #plt.close('all')
                    #print "Processing"
                    #print "size L: " + str(numpy.size(agents[instrument].values_R)) + " Size R: " + str(numpy.size(agents[instrument].values_L)) + " Size 
                    gestureList = getGestureSegments(agents[instrument], gestureList)


                    print "Gesture List size: " + str(numpy.size(gestureList))
                    #if numpy.size(gestureList) > 0:
                        #for i in xrange(numpy.size(gestureList)):
                            #smoothnesses = numpy.append(smoothnesses, gestureList[i].smoothness)
                            #smoothnesses = numpy.append(smoothnesses, gestureList[i].smoothness)
                            #print  "C: " + str(gestureList[i].centroid) + "S: " + str(gestureList[i].smoothness) + " E: " + str(gestureList[i].energy)# + " T: " + str(gestureList[i].type)
                            #print  "Smoothnessit: " + str(gestureList[i].smoothness)
                            #print  "Energyt: " + str(gestureList[i].energy)
                    #smooth_min = min(smoothnesses)
                    #smooth_max = max(smoothnesses)
                    #smooth_diff = smooth_max-smooth_min
                    #smooth_low = smooth_min + 0.33*smooth_diff
                    #smooth_mid = smooth_min + 0.66*smooth_diff
                    
                    
                    #print "S: " + str(smoothnesses)
                    #print "Diff: " + str(smooth_diff)
                    #print "Min MAX : " + str([smooth_min, smooth_max])
                    #print "Ranges: " + str([smooth_low, smooth_mid])


                        #print "Flatness: "  +str(gestureList[-1].flatness)
                    #plt.ion()
                    #plt.clf()
                    #for i in xrange(numpy.size(gestureList)):
                    #    #print "Feature 1: " + str(gestureList[i].feature_1)
                    #    #print "L: " + str(gestureList[i].data_L)
                    #    #print "R: " + str(gestureList[i].data_R)
                    #    print "i: " + str(i)
                    #    plt.figure(1)

                    #    # Do this in thread
                    #    plt.plot(gestureList[i].data_L)
                    #    plt.plot(gestureList[i].data_R, 'r')

                    #    plt.show(False)
                    #    plt.draw()

                    #    time.sleep(2)
                    #    plt.clf()
                    #    plt.cla()


                    #print "A Agenttien data: " + str(agents[instrument].values_L)
                    #plt.close('all')
                    #print "closed"
                    # Clear tables:
                    agents[instrument].values_R = []
                    agents[instrument].values_L = []
                    agents[instrument].centroid = []
                    agents[instrument].smoothness = []
                    agents[instrument].irregularity = []
                    agents[instrument].flatness = []

            if agents[instrument].manual == 0 and stuff[i+1] == 1:
                #print "Recording"
                agents[instrument].manual = stuff[i+1]



# These are needed for the OSC messages

s.addMsgHandler("/faceTrackState", faceTrackState_handler) 
s.addMsgHandler("/joint", jointXYZ_handler) 
s.addMsgHandler("/faceValue", faceValue_handler)
s.addMsgHandler("/bodyOrientation", bodyOrientation_handler)
s.addMsgHandler("/faceOrientation", faceOrientation_handler)
s.addMsgHandler("/handProximity", handProximity_handler)
s.addMsgHandler("/controlInput", controlInput_handler)
s.addMsgHandler("/agent1", agent_handler)
s.addMsgHandler("/agent2", agent_handler)
s.addMsgHandler("/agent3", agent_handler)

handLeft = joints("handLeft")
handTipLeft = joints("handTipLeft")
handTipRight = joints("handTipRight")
thumbLeft = joints("thumbLeft")
thumbRight = joints("thumbRight")
handLeft = joints("handLeft")
handRight = joints("handRight")
wristLeft = joints("wristLeft")
wristRight = joints("wristRight")
elbowLeft = joints("elbowLeft")
elbowRight = joints("elbowRight")
shoulderLeft = joints("shoulderLeft")
shoulderRight = joints("shoulderRight")
head = joints("head")
spineShoulder = joints ("spineShoulder")
neck = joints("neck")
spineBase = joints("spineBase")
spineMid = joints("spineMid")
jointVector = [handLeft, handRight, handTipLeft, handTipRight, wristLeft, wristRight, elbowLeft, elbowRight, shoulderLeft, shoulderRight, head, spineShoulder, neck, spineBase, spineMid]

movement = movements()
faceOrientation = faceOrientations()
facialFeature = facialFeatures()
bodyOrientation = bodyOrientations()
handProximity = handProximities()
controlInput = controlInputs()
faceTracker = faceTrackers()

agents = [0, agent_data(1), agent_data(2), agent_data(3)]

engagement = engagementData()

exit = 0


def main():
    global exit

    client = OSC.OSCClient()
    client.connect( ("localhost", 7111) ) # mihin osoitteeseen jne?
    msg = OSC.OSCMessage("/start")
    msg.append("bang")

    client.send(msg)


spectrum = [0, 0, 0]
musicSpace = musicalSpace()

def musicalSpaceCheck():
    forever = 1
    while forever == 1:
        smoothness = [0, 0, 0]  
        irregularity = [0, 0, 0]    
        flatness = [0, 0, 0]  
        centroid = [0, 0, 0]
        energy = [0, 0, 0]

        # Spectral centroid
        for i in xrange(1,4):
            if numpy.size(agents[i].centroid_mus) > 0:
                mean_centroid = numpy.mean(agents[i].centroid_mus)
                if mean_centroid < agents[i].centroid_ranges[0] and mean_centroid > 0:
                    centroid[i-1] = "low"
                elif mean_centroid > agents[i].centroid_ranges[0] and mean_centroid < agents[i].centroid_ranges[1]:
                    centroid[i-1] = "mid"
                elif mean_centroid > agents[i].centroid_ranges[1]:
                    centroid[i-1] = "high"
                agents[i].centroid_mus = [] # Reset vector
            else:
                centroid[i-1] = 0
      
        # Energy
            if numpy.size(agents[i].energy_mus) > 0:
                mean_energy = numpy.array(agents[i].energy_mus)
                mean_energy = 0.000020*10**(mean_energy/20)
                mean_energy = numpy.mean(mean_energy)
                mean_energy = 20*numpy.log10(mean_energy/0.000020)   
                if mean_energy < agents[i].energy_ranges[0] and mean_energy > 0:
                    energy[i-1] = "low"
                elif mean_energy >= agents[i].energy_ranges[0] and mean_energy < agents[i].energy_ranges[1]:
                    energy[i-1] = "mid"
                elif mean_energy > agents[i].energy_ranges[1]:
                    energy[i-1] = "high"
                agents[i].energy_mus = [] # Reset vector
            else:
                energy[i-1] = 0
                      
        # Smoothness
            if numpy.size(agents[i].smoothness_mus) > 0:
                mean_smoothness = numpy.mean(agents[i].smoothness_mus)
                if mean_smoothness > agents[i].smoothness_ranges[0]:
                    smoothness[i-1] = "low"
                elif mean_smoothness <= agents[i].smoothness_ranges[0] and mean_smoothness > agents[i].smoothness_ranges[1]:
                    smoothness[i-1] = "mid"
                elif mean_smoothness <= agents[i].smoothness_ranges[1]:
                    smoothness[i-1] = "high"
                agents[i].smoothness_mus = [] # Reset vector
            else:
                smoothness[i-1] = 0
        #print "smoothness: " + str(smoothness)
        
        musicSpace.centroid = centroid # " ['low', 0, 'high']
        musicSpace.smoothness = smoothness
        musicSpace.energy = energy
        
        #print "musicspace centroid: " + str(musicSpace.centroid)
        #print "musicspace smoothness: " + str(musicSpace.smoothness)
        #print "musicspace energy: " + str(musicSpace.energy)
      
        time.sleep(1)


def ticker100ms():
    global activity # katso tarvitaanko tama
    while exit == 0:
        time.sleep(0.1)
        #print "faceState: "+ str(faceTracker.state) + " " + str(faceOrientation.pointOfInterest)
        #print faceOrientation.pointOfInterest
        #pointOfInterestCollector(faceOrientation, faceTracker)
        #faceDataCollector(facialFeature, faceTracker)
        #trunkLeanCollector(bodyOrientation)
        #headOrientationCollector(bodyOrientation)
        #bodycenterPosCollector(spineMid)
        #print "SPINE MID X: " + str(spineMid.x)
        #asyncMovementCollector(movement, jointVector, controlInput) # controlInput!
        if (faceTracker.state == 1):
            engSample = engagement.calculate(facialFeature.lipCornerDepressorLeft, handTipLeft.duration, spineShoulder.acc, bodyOrientation.leanY, activity, neck.acc, wristRight.duration, head.acc, shoulderRight.acc)
            engagementCollector(engSample)
            #print "engagement Sample: " + str(engSample)
            engagement.buffer = numpy.append(engagement.buffer, engSample)

            # Keraa dataa 100ms valein 5 sekunnin bufferiin
            # engagementBuffer.append(value)
            # engagementBufferi.poistaEka

def ticker1000ms():
    global eng, activity
    while exit == 0:
        time.sleep(1)
        
        activity = 0
        for n in range(1,4):
            activity = activity + activita.activity(agents[n].values_R[0:100]) + activita.activity(agents[n].values_L[0:100]) 
        
        if (faceTracker.state == 1):
            eng = engagement.calculate(facialFeature.lipCornerDepressorLeft, handTipLeft.duration, spineShoulder.acc, bodyOrientation.leanY, activity, neck.acc, wristRight.duration, head.acc, shoulderRight.acc)
            #print eng

engagementMean = 80
# Tee tama joka 5. sekuntti
def engagementStates():
    global engagementMean
    while exit == 0:
        time.sleep(5)
        #print "buffer: "  + str(engagement.buffer)
        #print "buffer Size: " + str(engagement.buffer.size)
        # Require at least 10 values (1 second)
        if (engagement.buffer.size) > 5:

            engagementMean = numpy.mean(engagement.buffer)

            if (engagementMean < engagement.global_min):
                engagement.global_min = engagementMean
            if (engagementMean > engagement.global_max):
                engagement.global_max = engagementMean
            
            #print "min: " + str(engagement.global_min) + " max: " + str(engagement.global_max)
            engagement.meanValues = numpy.append(engagement.meanValues, engagementMean)
            engagement.meanValuesNormalized = engagement.meanValues - engagement.global_min
            minMaxRange = engagement.global_max - engagement.global_min
            #print "Min-max range: " + str(minMaxRange)

            if (minMaxRange != 0):
                engagement.meanValuesNormalized = engagement.meanValuesNormalized / minMaxRange
                # Trend and third
                eng_size = numpy.size(engagement.meanValuesNormalized) 

                if (eng_size > 1):

                    # Trend:
                    if (engagement.meanValuesNormalized[-1] > engagement.meanValuesNormalized[-2]):
                        engagement.trend = numpy.append(engagement.trend, 1)
                    elif (engagement.meanValuesNormalized[-1] < engagement.meanValuesNormalized[-2]):
                        engagement.trend = numpy.append(engagement.trend, -1)
                    elif (engagement.meanValuesNormalized[-1] == engagement.meanValuesNormalized[-2]):
                        engagement.trend = numpy.append(engagement.trend, 0)
    
                    
                    low_range = minMaxRange*0.40 + engagement.global_min
                    mid_range = minMaxRange*0.66 + engagement.global_min
                    #high_range = mid_range = minMaxRange*0.66 + engagement.global_min
                    #low_range = [engagement.global_min, engagement.global_min + low_range]

                    #mid_range = minMaxRange/4
                    #mid_range = [low_range[1], low_range[1] + mid_range]

                    #high_range = [mid_range[1], engagement.global_max]



                    # third:
                    latest_eng = engagement.meanValues[-1]


                    #print "Latest engagement: " + str(latest_eng)  + " Latest engagement norm: "  + str(engagementMean)
                    if (latest_eng < low_range):
                        engagement.third = numpy.append(engagement.third, "low")
                    elif (latest_eng >= low_range and latest_eng < mid_range):
                        engagement.third = numpy.append(engagement.third, "mid")
                    elif (latest_eng >= mid_range):
                        engagement.third = numpy.append(engagement.third, "high")
                    #print engagement.meanValues
        #if numpy.size(engagement.meanValuesNormalized)>10:
        #    eng_sorted = sorted(engagement.meanValuesNormalized)
        #    #print "eng sorted: " + str(eng_sorted)
       
        #    if eng_sorted[-1]-eng_sorted[-2] > 0.3:
        #        for i in xrange(numpy.size(engagement.meanValuesNormalized)):
        #            if engagement.meanValuesNormalized[i] == eng_sorted[-1]:
        #                engagement.meanValuesNormalized = numpy.delete(engagement.meanValuesNormalized, i)
        #                engagement.global_max = eng_sorted[-2]
                
                    
                                
                #del engagement.meanValuesNormalized[-1]
        #print "eng max: " + str(eng_sorted[-1]) eng 


        # Finally: clear the 5 second engagement buffer
        engagement.buffer = numpy.zeros(0)
        #print "Trend: " + str(engagement.trend)
        #print "faceState: "+ str(faceTracker.state) + 
        #print "Mean: " + str(engagement.meanValues)
        #print "Normalized: " + str(engagement.meanValuesNormalized)
        print "Third: "  + str(engagement.third)

def emgRead():
    global emg, activeAgent
    filename = "emg.csv"  
    while exit == 0:
        try:
            time.sleep(0.01)
            file = open(filename, 'r')
            lines = file.readlines()           
            last_row = lines[0]
            a = last_row.partition(',')
            a = a[2]
            a = a.split(",")      
            msg_emg = OSC.OSCMessage() 
            for i in xrange(8):
                msg_emg.append(int(a[i]))
            msg_emg.setAddress("/emg")
            for i in xrange(3):
                clients[i+1].send(msg_emg)

            file.close()
        except:
            pass
        

RFR = 0.5 # alkuarvo
gesturePlaybackOn = 0

def responseFrequencyRatio():
    global RFR, engagementMean, gesturePlaybackOn    
    # Pitaa kirjaa RFR:sta. Paivittaa sita engagement-tasojen perusteella
    while exit == 0:
        if gesturePlaybackOn == 1:
            first_eng = engagementMean
            time.sleep(5)
            last_eng = engagementMean
            diff_eng = last_eng - first_eng
            if (diff_eng > 0):
                RFR = RFR - 0.2
            elif (diff_eng < 0):
                RFR = RFR + 0.2
        time.sleep(0.1)


def findGesture(targetCentroid, targetSmoothness, targetEnergy): # low high -> high
    print "Find gesture - targetEnergy: " + str(targetEnergy) + " targetCentroid: " + str(targetCentroid) + " targetSmoothness: " + str(targetSmoothness)
    gestureCandidate = []
    listSize = numpy.size(gestureList)

    

    if (listSize > 0):
        for i in xrange(listSize):
            #print "i: " + str(i)
            if gestureList[i].centroid == targetCentroid:
                #print "gesture properties C: " + str(gestureList[i].centroid) +  " S: " + str(gestureList[i].smoothness) + " E: " + str(gestureList[i].energy)
                ##print "centroid"
                for j in xrange(numpy.size(targetSmoothness)):
                    if gestureList[i].smoothness == targetSmoothness[j]:

                #for k in xrange(numpy.size(targetEnergy)):
                #    if gestureList[i].energy == targetEnergy[k]: 

                ##                print "Gesture smoothness: " + str(gestureList[i].smoothness)
                ##                print "Gesture smoothness: " + str(gestureList[i].energy)
                        gestureCandidate.append(gestureList[i])

    print "Candidate size: " + str(numpy.size(gestureCandidate))

    listSize = numpy.size(gestureCandidate)
    if (listSize  > 0):
        for i in xrange(listSize):
            x = random.randint(0,listSize-1)
            agent_num = gestureCandidate[x].agent_num
            if agents[agent_num].manual == 0:
                return gestureCandidate[x]




def playGesture(gesture):

    #print "size : " + str(numpy.size(gesture))
    
    agent_num = gesture.agent_num
    if agents[agent_num].device_state == 1:
        print "playing gesture"

        agents[agent_num].prevMove = "CPU"
        print "agent: " + str(agent_num)
    
        #gesture.flatness
        msg_L = OSC.OSCMessage()
        msg_R = OSC.OSCMessage()
        msg_done = OSC.OSCMessage()
        msg_L.setAddress("/left")
        msg_R.setAddress("/right")
        msg_done.setAddress("/gestureDone")

        size_L = numpy.size(gesture.data_L)
        size_R = numpy.size(gesture.data_R)
        size = numpy.max([size_L, size_R])
        print "Current L before: " + str(agents[agent_num].current_L)

        print "size L : " + str(size_L) + " R: " + str(size_R)
        for i in xrange(size):

            #print "L:" + str(gesture.data_L[i]) + " R: " + str(gesture.data_R[i])
            if i < size_L:
                msg_L.append(gesture.data_L[i])
                clients[agent_num].send(msg_L)
                msg_L.pop(-1)
                last_L_i = i

            if i < size_R:
                msg_R.append(gesture.data_R[i])
                clients[agent_num].send(msg_R)
                msg_R.pop(-1)
                last_R_i = i
        

            time.sleep(0.01)
    
        msg_done.append("bang")
        clients[agent_num].send(msg_done)

        agents[agent_num].current_L = gesture.data_L[last_L_i]
        agents[agent_num].current_R = gesture.data_R[last_R_i]
        
def gesturePlayback(tempo):
    global RFR, gesturePlaybackOn
    print "gesture Playback On: " + str(gesturePlaybackOn)

    try:
        if gesturePlaybackOn == 0:
            gesturePlaybackOn = 1
            # Based on engagement state (ES) (L, M, H) and Response Frequency Ratio (RFR) [0,1]

            targetCentroid = ["low", "mid", "high"]
            targetSmoothness = ["low", "mid", "high"]
            targetEnergy = ["low", "mid", "high"]

            #print "Music Space centroids: " + str(musicSpace.centroid)

            for i in xrange(3):
                if musicSpace.centroid[i] == "low":
                    targetCentroid[0] = 0
                if musicSpace.centroid[i] == "mid":
                    targetCentroid[1] = 0
                if musicSpace.centroid[i] == "high":
                    targetCentroid[2] = 0
            
            targetCentroid = [i for i in targetCentroid if i != 0]
            #print targetCentroid

            if numpy.size(targetCentroid > 0):
                if numpy.size(targetCentroid > 1):
                    if targetCentroid[0] == "mid":
                        targetCentroid = "high"
                    elif targetCentroid[1] == "mid":
                        targetCentroid = "low"
                    else:
                        x = random.randint(0,1)
                        targetCentroid = targetCentroid[x]
                else:
                    targetCentroid = targetCentroid[0]
        

            #print "Music Space smoothness: " + str(musicSpace.smoothness)
            for i in xrange(3):
                if musicSpace.smoothness[i] == "low":
                    targetSmoothness[0] = 0
                if musicSpace.smoothness[i] == "mid":
                    targetSmoothness[1] = 0
                if musicSpace.smoothness[i] == "high":
                    targetSmoothness[2] = 0
            targetSmoothness = [i for i in targetSmoothness if i != 0]
            #print "Target Smoothness 1: " + str(targetSmoothness)

            #if numpy.size(targetSmoothness > 0):
            #    if numpy.size(targetSmoothness > 1):
            #        if targetSmoothness[0] == "mid":
            #            targetSmoothness = "high"
            #        elif targetSmoothness[1] == "mid":
            #            targetSmoothness = "low"
            #        else:
            #            x = random.randint(0,1)
            #            targetSmoothness = targetSmoothness[x]
            #    else:
            #        targetSmoothness = targetSmoothness[0]

            #print "Target Smoothness 2: "  + str(targetSmoothness)

            #print "Music Space energy: " + str(musicSpace.energy)

            for i in xrange(3):
                if musicSpace.energy[i] == "low":
                    targetEnergy = 'low'
                    break
                if musicSpace.energy[i] == "mid":
                    targetEnergy = 'low'
                    break
                if musicSpace.energy[i] == "high":
                    targetEnergy[2] = 0

            if numpy.size(targetEnergy) > 1:
                targetEnergy = [i for i in targetEnergy if i != 0]
            
           #print "Target energy 1: " + str(targetEnergy)

            #print "---"
            #print "[Scene] Centroid: " + str(musicSpace.centroid) + ", Smoothness: " + str(musicSpace.smoothness) + ", Energy: " + str(musicSpace.energy) 
            #print "[Targets] Centroid: " + str(targetCentroid) + ", Smoothness: " + str(targetSmoothness) + ", Energy: " + str(targetEnergy)        
            #print "---"



            # playing mid: options:  low, high
            # -> choose randomly

            #gesture_test = findGesture(targetCentroid, targetSmoothness, targetEnergy)
            #if gesture_test != None:
            #    print "[Gesture] Centroid: " + str(gesture_test.centroid) + ", Smoothness: " + str(gesture_test.smoothness) + ", Energy: " + str(gesture_test.energy)
            #return
        
            # Low & mid -> low
            # High & mid -> high                
            #if eng_state == "low":

            x1 = random.randint(0,100)/100.
            x2 = random.randint(0,100)/100.
            
            try:
                #print "LAST THIRD: "  + str(engagement.third[-1])
                if engagement.third[-1] == "low":
                    RFR = 0.9
                elif engagement.third[-1] == "mid":
                    RFR = 0.6
                elif engagement.third[-1] == "high":
                    RFR = 0.2
            except:
                eng_state = 0.5
            

            print "RFR: "  + str(RFR) + " x1: " + str(x1) + " x2: " + str(x2)
            if ( x1 < RFR):# RFR ):

                print "Produce gesture 1"
                gesture_1 = findGesture(targetCentroid, targetSmoothness, targetEnergy)
                if gesture_1 != None:
                    playGesture(gesture_1)
                    time.sleep(tempo/1000.)
                if (x2 < RFR):
                    print "Produce gesture 2"
                    gesture_2 = findGesture(targetCentroid, targetSmoothness, targetEnergy)
                    if gesture_2 != None:
                        playGesture(gesture_2)


            time.sleep(tempo/1000.)
            gesturePlaybackOn = 0
            #   1. Check ES
                # Low state:
                #   1. Monitor energy offsets
                #   2. Check RFRs
                #   3.1 Find 1st gesture with contrasting features
                #   3.2 Find 2nd gesture with contrasting features
                #   4.1 Playback first gesture
                #   4.2 Send timestamp to RFR function (gather current engagement, compare to 5 second after)
                #   4.3 Playback 2nd gesture after TEMPO ms
                #   


                # Mid state:
                #   1. Monitor energy offsets & attacks

                # 

                #   2. Check RFR & calculate
                #   3. Find gesture with contrasting features

                # High state:
                #   1. 
    except:
        gesturePlaybackOn = 0
#################
# Threads            
# Start the OSC server
#print "\nStarting OSCServer. Use ctrl-C to quit."    
st = threading.Thread( target = s.serve_forever )
st.start()

thread.start_new_thread(musicalSpaceCheck, ( ))
#thread.start_new_thread(responseFrequencyRatio, ( ))

#thread.start_new_thread(tickerAgent, (1, ))
#thread.start_new_thread(tickerAgent, (2, ))
#thread.start_new_thread(tickerAgent, (3, ))

thread.start_new_thread(ticker100ms, ( ))
thread.start_new_thread(ticker1000ms, ( ))
thread.start_new_thread(engagementStates, ( ))
thread.start_new_thread(emgRead, ( ))


#thread.start_new_thread(tickerCluster, (1, ))
#thread.start_new_thread(tickerCluster, (2, ))
#thread.start_new_thread(tickerCluster, (3, ))
if __name__ == "__main__":
	main()
