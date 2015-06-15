import time, threading
from threading import Timer
import thread
import OSC
from array import *
import numpy
import sys
import os
import math
import random
import string
from numpy import isnan
from math import isnan, isinf
from datetime import datetime
from dataCollectors import *
from gestureProcessing import *
from classes import *


lastInstrument = 0
automation = 1
engSample = 0
emg = 0
activity = 0
totalAcc = 0

gestureList = []

# OSC clients
clients = [0, OSC.OSCClient(), OSC.OSCClient(), OSC.OSCClient()]
clients[1].connect( ('10.0.0.1', 9000) ) 
clients[2].connect( ('10.0.0.2', 9000) ) 
clients[3].connect( ('10.0.0.3', 9000) ) 

# OSC server IP and port
receive_address = '10.0.0.4', 9000

s = OSC.ThreadingOSCServer(receive_address)
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
    state = stuff[0]
    if (faceTracker.state == 0 and state == 1):
        faceTracker.state = state
        faceStateCollector(state)


    if (faceTracker.state == 1 and state == 0):
        faceTracker.state = state
        faceStateCollector(state)

def jointXYZ_handler(addr, tags, stuff, source):
    msgSize = numpy.size(stuff)
    totalAcc = 0
    for i in xrange(msgSize):
        try:
            if (stuff[i] == "handTipLeft"):
                acc = handTipLeft.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc

            if (stuff[i] == "handTipRight"):
                acc = handTipRight.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc

            if (stuff[i] == "wristLeft"):
                acc = wristLeft.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc
                           
            if (stuff[i] == "wristRight"):
                acc = wristRight.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc

            if (stuff[i] == "handLeft"):
                acc = handLeft.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + handLeft.acc         

            if (stuff[i] == "handRight"):
                acc = handRight.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
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
                totalAcc = totalAcc + head.acc    
                        
            if (stuff[i] == "spineShoulder"):
                acc = spineShoulder.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc

            if (stuff[i] == "neck"):
                acc = neck.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + neck.acc

            if (stuff[i] == "spineMid"):
                acc = spineMid.calcAcc(stuff[i+1], stuff[i+2], stuff[i+3])
                totalAcc = totalAcc + acc
        except:
            pass
    totalAccCollector(totalAcc)


def handProximity_handler(addr, tags, stuff, source):
    # Not used
    pass

def process_input(instrument, hand, value):
    global lastInstrument, emg_norm, activity

    if hand == "left":       
        if agents[instrument].manual == 1:
            lastInstrument = instrument

            if agents[instrument].device_state == 0 and value > 30:
                print "INSTRUMENT: " + str(instrument) + " ON"
                agents[instrument].device_state = 1
            agents[instrument].current_L = value
            agents[instrument].values_L = numpy.insert(agents[instrument].values_L, 0, value) # add first
            agents[instrument].prevMove = "user"
            agents[instrument].emg = numpy.insert(agents[instrument].emg, 0, emg_norm)

            engSample = 0
            if (faceTracker.state == 1):
                engSample = engagement.calculate(facialFeature.lipCornerDepressorLeft, handTipLeft.duration, spineShoulder.acc, bodyOrientation.leanY, activity, neck.acc, wristRight.duration, head.acc, shoulderRight.acc)
                agents[instrument].engagement = numpy.insert(agents[instrument].engagement, 0, engSample)
          
    if hand == "right":       
        if agents[instrument].manual == 1:
            lastInstrument = instrument
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
    global prev_energy, tempo, engagementMean

    # For gesture recording
    if agents[instrument].manual == 1:
        if feature == "centroid":
            if isnan(value) == 0 and value != 0:
                agents[instrument].centroid = numpy.insert(agents[instrument].centroid, 0, value)
        if feature == "smoothness":
            if value != 0:
                agents[instrument].smoothness = numpy.insert(agents[instrument].smoothness, 0, value)
        if feature == "energy":
            if isnan(value) == 0 and value != 0:
                agents[instrument].energy = numpy.insert(agents[instrument].energy, 0, value)

    # For the musical scene analysis of each agent
    if feature == "smoothness":
        if value != 0:
            agents[instrument].smoothness_mus = numpy.insert(agents[instrument].smoothness_mus, 0, value)
    if feature == "centroid":
        if isnan(value) == 0 and value != 0:
            agents[instrument].centroid_mus = numpy.insert(agents[instrument].centroid_mus, 0, value)
    if feature == "energy":
        if isnan(value) == 0 and value > 0:
            agents[instrument].energy_mus = numpy.insert(agents[instrument].energy_mus, 0, value)

   # Gesture playback triggers:
    if agents[instrument].prevMove == "user":
        
        # Sound tail
        if feature == "energy":
            # Onset
            if value < agents[instrument].energy_low:
                if agents[instrument].prev_energy == "on":
                    agents[instrument].prev_energy = "off"
                    gesturePlayback(tempo)
            # Offset
            if value > agents[instrument].energy_high:
                if agents[instrument].prev_energy == "off":
                    agents[instrument].prev_energy = "on"
  
        # Every third detected attack                                                
        if feature == "attack3":
            if value == 1:
                try:
                    eng_state = engagement.third[-1]
                    if engagement.third[-1] == "mid" or engagement.third[-1] == "high":# or eng_state == "high" or eng_state == "low":
                        gesturePlayback(tempo)
                except:
                    pass

        # Every sixth detected attack 
        if feature == "attack6":
            if value == 1:
                try:
                    print "attack6 + third: "  + str(engagement.third[-1])
                    eng_state = engagement.third[-1]
                    if engagement.third[-1] == "high":
                        gesturePlayback(tempo)
                except:
                    pass                          
        if feature == "tempo":
            tempo = value


     
def agent_handler(addr, tags, stuff, source):
    global gestureList
    instrument = addr[-1]
    instrument = string.atoi(instrument)

    size = numpy.size(stuff)

    for i in xrange(size):
        if stuff[i] == "left":
            process_input(instrument, "left", stuff[i+1])
        if stuff[i] == "right":
            process_input(instrument, "right", stuff[i+1])
        if stuff[i] == "smoothness":
            process_features(instrument, "smoothness", stuff[i+1]) 
        if stuff[i] == "irregularity":
            process_features(instrument, "irregularity", stuff[i+1])
        if stuff[i] == "flatness":
            process_features(instrument, "flatness", stuff[i+1])
        if stuff[i] == "centroid":
            process_features(instrument, "centroid", stuff[i+1])
        if stuff[i] == "energy":
            process_features(instrument, "energy", stuff[i+1])
        if stuff[i] == "attack3":
            process_features(instrument, "attack3", stuff[i+1])
        if stuff[i] == "attack6":
            process_features(instrument, "attack6", stuff[i+1])
        if stuff[i] == "tempo":
            process_features(instrument, "tempo", stuff[i+1])
        if stuff[i] == "manual":
            if agents[instrument].manual == 1 and stuff[i+1] == 0:
                agents[instrument].manual = 0

                if numpy.size(agents[instrument].values_L) > 10:
                    gestureList = getGestureSegments(agents[instrument], gestureList)
                    print "Gesture List size: " + str(numpy.size(gestureList))

                    # Reset vectors
                    agents[instrument].values_R = []
                    agents[instrument].values_L = []
                    agents[instrument].centroid = []
                    agents[instrument].smoothness = []
                    agents[instrument].engagement = []
                    agents[instrument].energy = []
                    agents[instrument].emg = []

            if agents[instrument].manual == 0 and stuff[i+1] == 1:
                agents[instrument].manual = stuff[i+1]

s.addMsgHandler("/faceTrackState", faceTrackState_handler) 
s.addMsgHandler("/joint", jointXYZ_handler) 
s.addMsgHandler("/faceValue", faceValue_handler)
s.addMsgHandler("/bodyOrientation", bodyOrientation_handler)
s.addMsgHandler("/faceOrientation", faceOrientation_handler)
s.addMsgHandler("/handProximity", handProximity_handler)
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
faceTracker = faceTrackers()

agents = [0, agent_data(1), agent_data(2), agent_data(3)]

engagement = engagementData()

exit = 0


def main():
    global exit
    print "Running - NOISA reponse"
    client = OSC.OSCClient()
    client.connect( ("localhost", 7111) )
    msg = OSC.OSCMessage("/start")
    msg.append("bang")

    client.send(msg)

    filename = 'noisa_start.txt'
    file = open(filename, 'a')
    file.write("Time: " + str(time.time()) + '\n')
    file.close()


spectrum = [0, 0, 0]
musicSpace = musicalSpace()

def musicalSpaceCheck():
    forever = 1
    while forever == 1:
        smoothness = [0, 0, 0]  
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
        
        musicSpace.centroid = centroid # " ['low', 0, 'high']
        musicSpace.smoothness = smoothness
        musicSpace.energy = energy
        
        #print "musicspace centroid: " + str(musicSpace.centroid)
        #print "musicspace smoothness: " + str(musicSpace.smoothness)
        #print "musicspace energy: " + str(musicSpace.energy)
      
        time.sleep(1)


def ticker100ms():
    global activity, engSample
    while exit == 0:
        time.sleep(0.1)

        if (faceTracker.state == 1):
            engSample = engagement.calculate(facialFeature.lipCornerDepressorLeft, handTipLeft.duration, spineShoulder.acc, bodyOrientation.leanY, activity, neck.acc, wristRight.duration, head.acc, shoulderRight.acc)
            engagement.buffer = numpy.append(engagement.buffer, engSample)

            filename = 'noisa_eng_raw.txt'
            file = open(filename, 'a')
            file.write("Time: " + str(time.time()) + " " + str(engSample) + '\n')
            file.close()


            # Keraa dataa 100ms valein 5 sekunnin bufferiin
            # engagementBuffer.append(value)
            # engagementBufferi.poistaEka


def activityCalc(indata):
    resamp_data = []
    data_length = int(numpy.floor(len(indata) / 10))
    for i in xrange(data_length):
        resamp_data.append(numpy.mean(indata[i*10:(i+1)*10]))
    resamp_data = numpy.subtract(resamp_data[1:-1], resamp_data[0:-2])
    return numpy.mean(numpy.abs(resamp_data)) if len(resamp_data) > 0 else 0

def activitySampler():
    global activity
    while exit == 0:
        time.sleep(1)
        
        activity = 0
        for n in range(1,4):
            activity = activity + activityCalc(agents[n].values_R[0:100]) + activityCalc(agents[n].values_L[0:100]) 
        print "activity: " + str(activity)

engagementMean = 80
# Tee tama joka 5. sekuntti
def engagementStates():
    global engagementMean
    while exit == 0:
        time.sleep(5)

        # Require at least 5 samples
        if (engagement.buffer.size) > 5:

            engagementMean = numpy.mean(engagement.buffer)
            if (engagementMean < engagement.global_min):
                engagement.global_min = engagementMean
            if (engagementMean > engagement.global_max):
                engagement.global_max = engagementMean
            
            engagement.meanValues = numpy.append(engagement.meanValues, engagementMean)
            engagement.meanValuesNormalized = engagement.meanValues - engagement.global_min
            minMaxRange = engagement.global_max - engagement.global_min

            if (minMaxRange != 0):
                engagement.meanValuesNormalized = engagement.meanValuesNormalized / minMaxRange
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

                    latest_eng = engagement.meanValues[-1]

                    if (latest_eng < low_range):
                        engagement.third = numpy.append(engagement.third, "low")
                    elif (latest_eng >= low_range and latest_eng < mid_range):
                        engagement.third = numpy.append(engagement.third, "mid")
                    elif (latest_eng >= mid_range):
                        engagement.third = numpy.append(engagement.third, "high")

        # Finally: clear the 5 second engagement buffer
        engagement.buffer = numpy.zeros(0)

        #print "Mean: " + str(engagement.meanValues)
        #print "Normalized: " + str(engagement.meanValuesNormalized)
        #print "Third: "  + str(engagement.third)

        if numpy.size(engagement.meanValues) > 0 and numpy.size(engagement.meanValuesNormalized) > 0 and numpy.size(engagement.third) > 0:
            filename = 'noisa_eng_processed.txt'
            file = open(filename, 'a')
            file.write("Time: " + str(time.time()) + " mean " + str(engagement.meanValues[-1]) + " norm " + str(engagement.meanValuesNormalized[-1]) + " third " + str(engagement.third[-1]) + '\n')
            file.close()


emgMax = 5
emgMin = 10

emgBuffer = []
emg_norm = 0

def emgRead():
    global emg_norm, lastInstrument, emgMax, emgMin, emgBuffer
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
  
            emg = a[0]
            emg = numpy.abs(numpy.int(emg))
            emgBuffer = numpy.append(emgBuffer, emg) 
                       
            if numpy.size(emgBuffer) > 50:

                arvo = numpy.mean(emgBuffer)
                if arvo > emgMax*1.2:
                    emgMax = arvo*0.8
                
                if arvo < emgMin - 0.4:
                    emgMin = arvo + 0.2

                arvo3 = (arvo-emgMin)/(emgMax-emgMin)
                if arvo3 < 0:
                    arvo3 = 0
                emg_norm = (math.exp(arvo3)-1)/(math.e-1)
                if emg_norm > 1.1:
                    emg_norm = 1.1
                if emg_norm <= 0.3:
                    emg_norm = 0.3
                emgBuffer = []

                msg_emg = OSC.OSCMessage() 
                msg_emg.append(emg_norm)
                msg_emg.setAddress("/emg")

                for i in xrange(3):
                    if agents[i+1].manual == 1 or lastInstrument == i+1:
                        clients[i+1].send(msg_emg)

            file.close()
        except:
            pass
        

RFR = 0.5 # alkuarvo
gesturePlaybackOn = 0


def findGesture(targetCentroid, targetSmoothness, targetEnergy): # low high -> high
    print "Find gesture - targetEnergy: " + str(targetEnergy) + " targetCentroid: " + str(targetCentroid) + " targetSmoothness: " + str(targetSmoothness)
    gestureCandidate = []
    gestureCandidate_idx = []
    listSize = numpy.size(gestureList)

    if (listSize > 0):
        for i in xrange(listSize):
            if gestureList[i].centroid == targetCentroid:

                for j in xrange(numpy.size(targetSmoothness)):
                    if gestureList[i].smoothness == targetSmoothness[j]:
                        if agents[gestureList[i].agent_num].manual == 0:
                            gestureCandidate.append(gestureList[i])
                            gestureCandidate_idx.append(i)

    print "Candidate size: " + str(numpy.size(gestureCandidate))


    highest_eng = -1
    highest_eng_idx = -1

    listSize = numpy.size(gestureCandidate)
    if (listSize  > 0):
        for i in xrange(listSize):
            print "Candidate engagement: " + str(gestureCandidate[i].engagement)
            if gestureCandidate[i].engagement > highest_eng:
                highest_eng = gestureCandidate[i].engagement
                highest_eng_idx = i

        listIdx = gestureCandidate_idx[highest_eng_idx]
        gestureList[listIdx].n_plays = gestureList[listIdx].n_plays + 1
        if gestureList[listIdx].n_plays == 3:
            del gestureList[listIdx]
        return gestureCandidate[highest_eng_idx]



def playGesture(gesture):
    
    agent_num = gesture.agent_num
    if agents[agent_num].device_state == 1:
        print "playing gesture"

        agents[agent_num].prevMove = "CPU"
        print "agent: " + str(agent_num)
    
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

        filename = 'noisa_gesturePlayback.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + '\n')
        file.close()

        agents[agent_num].current_L = gesture.data_L[last_L_i]
        agents[agent_num].current_R = gesture.data_R[last_R_i]
        
def gesturePlayback(tempo):
    global gesturePlaybackOn
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
        
            for i in xrange(3):
                if musicSpace.smoothness[i] == "low":
                    targetSmoothness[0] = 0
                if musicSpace.smoothness[i] == "mid":
                    targetSmoothness[1] = 0
                if musicSpace.smoothness[i] == "high":
                    targetSmoothness[2] = 0
            targetSmoothness = [i for i in targetSmoothness if i != 0]


            print "Target Smoothness 1: " + str(targetSmoothness)

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
            
            print "Target energy 1: " + str(targetEnergy)

            #print "---"
            #print "[Scene] Centroid: " + str(musicSpace.centroid) + ", Smoothness: " + str(musicSpace.smoothness) + ", Energy: " + str(musicSpace.energy) 
            #print "[Targets] Centroid: " + str(targetCentroid) + ", Smoothness: " + str(targetSmoothness) + ", Energy: " + str(targetEnergy)        
            #print "---"

            x1 = random.randint(0,100)/100.
            x2 = random.randint(0,100)/100.


            try:
                if engagement.third[-1] == "low":
                    RFR = 0.9
                elif engagement.third[-1] == "mid":
                    RFR = 0.6
                elif engagement.third[-1] == "high":
                    RFR = 0.3
            except:
                RFR = 0.5
            
  
            if ( x1 < RFR):

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

                #   1. Monitor energy offsets
                #   2. Set RFR according to engagement state
                #   3.1 Find 1st gesture with contrasting features
                #   3.2 Find 2nd gesture with contrasting features
                #   4.1 Playback first gesture
                #   4.2 Send timestamp to RFR function (gather current engagement, compare to 5 second after)
                #   4.3 Playback 2nd gesture after TEMPO ms
  

    except:
        gesturePlaybackOn = 0
#################
# Threads            
# Start the OSC server
#print "\nStarting OSCServer. Use ctrl-C to quit."    
st = threading.Thread( target = s.serve_forever )
st.start()

thread.start_new_thread(musicalSpaceCheck, ( ))
thread.start_new_thread(ticker100ms, ( ))
thread.start_new_thread(activitySampler, ( ))
thread.start_new_thread(engagementStates, ( ))
thread.start_new_thread(emgRead, ( ))


if __name__ == "__main__":
	main()
