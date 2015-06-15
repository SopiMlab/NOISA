import numpy

from scipy.signal import lfilter
from peakdetect import peakdetect
import matplotlib.pyplot as plt
from classes import *


gesture_minlength_threshold = 30
gesture_maxlength_threshold = 1000 # 5 sek on pitka
stationary_length = 1


def getStaticPoints(window, stationary_length = 20):


    static_start = []
    static_end = []
    static_points = 0
    n = 0;
    while(1):
        if n<=numpy.size(window)-stationary_length:   
            if window[n] == window[n+1]:
                stationary_value = window[n];
                if all(item == stationary_value for item in window[n:n+stationary_length]):
                    static_start.insert(static_points,n)                        
                    for endPoint in range(n, numpy.size(window)):
                        if window[endPoint] != stationary_value:
                            static_end.insert(static_points,endPoint-1)
                            static_points = static_points + 1
                            n = endPoint
                            break
                            
                        if endPoint == numpy.size(window)-1:
                            static_end.insert(static_points,endPoint)
                            n = endPoint
                            break
            n = n+1;    
        else:
            break
    return static_start, static_end





def combineShortGestures(gestures):
    len_g = len(gestures)-1
    if len_g > 0:
        for i in xrange(len_g):
            if gestures[i][1] == gestures[i+1][0]:
                if gestures[i][1] - gestures[i][0] < 30 or gestures[i+1][1] - gestures[i+1][0] < 30:
                    gestures[i][1] = gestures[i+1][1]
                    gestures.pop(i+1)
                    return(combineShortGestures(gestures))
    return gestures



def addGesture(gestureList, agent, L_start, L_end, R_start, R_end, type):

    data_L = agent.values_L[L_start:L_end]
    data_R = agent.values_R[R_start:R_end]

    gesture_min_length = 15 # 15 samples

    try:
        engagement = agent.engagement[L_start:L_end]
        if numpy.size(engagement) > 0:
            engagement = numpy.mean(engagement)
        else:
            engagement = -1
    except:
        return gestureList

    try:
        emg = agent.emg[L_start:L_end]
        if numpy.size(emg) > 0:
            emg = numpy.mean(emg)
    except:
        return gestureList

    try:
        centroid = agent.centroid[R_start:R_end]
        if numpy.size(centroid) > 0:
            centroid = numpy.mean(centroid)

            if centroid < agent.centroid_ranges[0]:
                centroid = "low"
            elif centroid >= agent.centroid_ranges[0] and centroid < agent.centroid_ranges[1]:
                centroid = "mid"
            elif centroid >= agent.centroid_ranges[1]:
                centroid = "high"
        else:
            return gestureList                
    except:
        return gestureList

    try:
        energy = agent.energy[R_start:R_end]

        if numpy.size(energy) > 0:
            ener = numpy.array(energy)
            ener = 0.000020*10**(ener/20)
            ener = numpy.mean(ener)
            energy = 20*numpy.log10(ener/0.000020)
            if energy < agent.energy_ranges[0]:
                energy = "low"
            elif energy >= agent.energy_ranges[0] and energy < agent.energy_ranges[1]:
                energy = "mid"
            elif energy >= agent.energy_ranges[1]:
                energy = "high"
        else:
            return gestureList
    except:
        return gestureList

    try:
        smoothness = agent.smoothness[R_start:R_end]
        if numpy.size(smoothness) > 0:
            smoothness = numpy.mean(smoothness)
            if smoothness < agent.smoothness_ranges[0]:
                smoothness = "low"
            elif smoothness >= agent.smoothness_ranges[0] and smoothness < agent.smoothness_ranges[1]:
                smoothness = "mid"
            elif smoothness >= agent.smoothness_ranges[1]:
                smoothness = "high"
        else:
            return gestureList
    except:
        return gestureList
  

    if numpy.size(data_L) > gesture_min_length:
        gesture_new = gesture(data_L, data_R, centroid, energy, smoothness, engagement, emg, type, agent.agent_num)
        gestureList.append(gesture_new)
    
    return gestureList


def getGestureSegments(agent, gestureList): 
    
    window_L = agent.values_L
    window_R = agent.values_R
    
    gestures = []
    gestures_timestamps = []
    gestures_R = []

    fs = 100
    gesture_min_length = 15 # 15 samples

    if agent.agent_num == 1:
        static_max = 600 # < 350
    if agent.agent_num == 2:
        static_max = 600 # > 600
    if agent.agent_num == 3:
        static_max = 600

    gesture_threshold = 0.4; 
    gesture_threshold_samples = 30;
    sample_tail = 150 

    [static_start, static_end] = getStaticPoints(window_L, gesture_threshold_samples)
    
    ### Sustained gestures - handle on max position ###
    if numpy.size(static_start) > 0:
        for i in xrange(numpy.size(static_start)) :
            if window_L[static_start[i]] > static_max:
                L_start = static_start[i]
                R_start = L_start

                L_end = static_end[i]
                R_end = L_end          

                gestureList = addGesture(gestureList, agent, L_start, L_end, R_start, R_end, 'sustain')

    ### Normal gestures - left hand begins ####
    x = range(numpy.size(window_L))
    max, min = peakdetect(window_L, x, lookahead = 2)
    maxidx = [p[0] for p in max]
    minidx = [p[0] for p in min]    
    

    for i in xrange(numpy.size(minidx)):
        for k in xrange(numpy.size(static_start)):
            if minidx[i] == static_start[k]:
                minidx[i] = -1
    minidx = sorted(x for x in minidx if x > 0)    

    starting_points = numpy.unique(static_end + minidx)
    ending_points = numpy.unique(static_start + minidx)
    ending_points = numpy.append(ending_points, (numpy.size(window_L)-1))
   

    for i in xrange(numpy.size(starting_points)):
        starting_point = starting_points[i]
        ending_point = sorted(x for x in ending_points if x > starting_point)
        if numpy.size(ending_point) > 0:
            ending_point = ending_point[0]
            gestures.append([starting_point, ending_point])

    gestures = combineShortGestures(gestures)

    len_g = len(gestures)


    for i in xrange(len_g):
        L_start = gestures[i][0]
        L_end = gestures[i][1]
        R_start = gestures[i][0]

        if i == len(gestures)-1:
            if gestures[i][1] + sample_tail > numpy.size(window_R):
                R_end = numpy.size(window_R)
            else:
                R_end = gestures[i][1] + sample_tail
        
        else:
 
            if gestures[i+1][0] - gestures[i][1] > sample_tail:
                R_end = gestures[i][1] + sample_tail
            else:
                R_end = gestures[i+1][0]
        
        if R_end < gestures[i][1]:
            R_end = gestures[i][1]


        gestureList = addGesture(gestureList, agent, L_start, L_end, R_start, R_end, 'normal')


    return gestureList
