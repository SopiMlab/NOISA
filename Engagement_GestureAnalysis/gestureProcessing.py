import numpy

from scipy.signal import lfilter
from peakdetect import peakdetect
import matplotlib.pyplot as plt
from classes import *


gesture_minlength_threshold = 30
gesture_maxlength_threshold = 1000 # 5 sek on pitka
stationary_length = 1


def getStaticPoints(ikkuna, stationary_length = 20):

    #print ikkuna
    # stationary_length = 20;
    static_start = []
    static_end = []
    static_points = 0
    n = 0;
    while(1):
        #print "loopppi"
        if n<=numpy.size(ikkuna)-stationary_length:   
            # Nykyinen ja seuraava on samat
            if ikkuna[n] == ikkuna[n+1]:
                stationary_value = ikkuna[n];

                # Jos my?s 10 seuraavaa on samat niin station??risyys l?ytyi

                if all(item == stationary_value for item in ikkuna[n:n+stationary_length]):
                    #print "statio " + str(n)

                    static_start.insert(static_points,n)
                    # Etsi mihin station??risyys loppuu
                        
                    for loppukohta in range(n, numpy.size(ikkuna)):
                        #print "loppukohta: " + str(loppukohta) + " ikkunanokko: " + str(np.size(ikkuna))
                        if ikkuna[loppukohta] != stationary_value:
                            static_end.insert(static_points,loppukohta-1)
                            static_points = static_points + 1
                            n = loppukohta
                            #print "ei loppu"
                            break
                            
                        if loppukohta == numpy.size(ikkuna)-1:
                            #print "loppu"
                            static_end.insert(static_points,loppukohta)
                            n = loppukohta
                            break
              
            n = n+1;
        
        else:
            break

    #print "start: " + str(static_start) + " stop: " + str(static_end)
    return static_start, static_end





def combineShortGestures(gestures):
    len_g = len(gestures)-1
    if len_g > 0:
        for i in xrange(len_g):
            # 1. Gesturet on perakkain
            if gestures[i][1] == gestures[i+1][0]:
                if gestures[i][1] - gestures[i][0] < 30 or gestures[i+1][1] - gestures[i+1][0] < 30:
                    gestures[i][1] = gestures[i+1][1]
                    gestures.pop(i+1)
                    return(combineShortGestures(gestures))
    return gestures



def addGesture(gestureList, agent, start, end, type):
    data_L = agent.values_L[start:end]
    data_R = agent.values_R[start:end]

    
    try:
        smoothness = agent.smoothness[R_start:R_end]
        smoothness = numpy.mean(smoothness)
    except:
        smoothness = []
    
    try:
        irregularity = agent.irregularity[R_start:R_end]
        irregularity = numpy.mean(irregularity)
    except:
        irregularity = []
        
    try:
        flatness = agent.flatness[R_start:R_end]
        flatness = numpy.mean(flatness)
    except:
        flatness = []
                                         

    gesture_new = gesture(data_L, data_R, smoothness, irregularity, flatness, type, agent)
    gestureList.append(gesture_new)

    return gestureList





# Extract the gestures from raw data
# Return left and right hand information for each gesture
def getGestureSegments(agent, gestureList): 
    
    window_L = agent.values_L
    window_R = agent.values_R
    
    gestures = []
    gestures_timestamps = []
    gestures_R = []

    gestures_sustain = []

    
    #print "WINDOW L: " + str(window_L)

    fs = 100 # Arduino sampling rate ( 1 / t ) <=> [metro 10] ( 1 / 0.01s ) 
    #fs = 20

    #window_length = 5; #seconds
    #window_overlap = 0.2; 
    #window_samples = fs*window_length;
    #overlap_samples = numpy.floor(window_overlap*window_samples);
    #window_length_R = 6;
    #window_samples_R = fs*window_length_R;

    gesture_min_length_s = 0.15 #seconds
    gesture_min_length_n = numpy.ceil(fs*gesture_min_length_s)

    gesture_min_length = 15 # 15 samples

    # Kaksi perakkaista gesturea yhteen - ts. nopea edestakainen liike

    if agent.agent_num == 1:
        static_max = 600 # < 350
    if agent.agent_num == 2:
        static_max = 600 # > 600
    if agent.agent_num == 3:
        static_max = 600

    gesture_threshold = 0.4; # static time between two gestures (seconds)
    #gesture_threshold_samples = fs*gesture_threshold;

    gesture_threshold_samples = 30;
   # gesture_threshold_n = 2*gesture_min_length_n

    sample_tail = 150 # numpy.ceil(fs*1.5)# 

    [static_start, static_end] = getStaticPoints(window_L, gesture_threshold_samples)
    
    ### Sustained gestures - handle on max position ###
    # Etsi kohdat joissa staattinen && max arvo
        # Tallenna kaikki oikean kaden tieto
        # Tallenna myos vasen kasi max arvo
    if numpy.size(static_start) > 0:
        for i in xrange(numpy.size(static_start)) :
            #print "Static val: " + str(window_L[static_start[i]])
            if window_L[static_start[i]] > static_max:
                start = static_start[i]
                end = static_end[i]
                gestures_sustain.append([start, end])
                data_L = window_L[start:end]
                data_R = window_R[start:end]
                #print "centroid: " + str(agent.centroid)
                try:
                    centroid = agent.centroid[start:end]
                    if numpy.size(centroid) > 0:
                        centroid = numpy.mean(centroid)

                        if centroid < agent.centroid_ranges[0]:
                            centroid = "low"
                        elif centroid >= agent.centroid_ranges[0] and centroid < agent.centroid_ranges[1]:
                            centroid = "mid"
                        elif centroid >= agent.centroid_ranges[1]:
                            centroid = "high"
                    else:
                        print "centroid discard 1"
                        # If no centroid detected - discard the gesture
                        #pass
                        continue               
                except:
                    print "centroid discard 2"
                    # If no centroid detected - discard the gesture
                    #pass
                    continue

                try:
                    energy = agent.energy[start:end]

                    if numpy.size(energy) > 0:
                        #print "ENEG: " + str(energy)
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
                        print "energy discard 1"
                        # Discard
                        #pass
                        continue
                except:
                    print "energy discard 2"
                    # Discard
                    #pass
                    continue

                try:
                    smoothness = agent.smoothness[start:end]
                    #print "smoothness orig: " + str(smoothness)
                    #smoothness = filter(lambda x: x != 0, smoothness)
                    if numpy.size(smoothness) > 0:
                        smoothness = numpy.mean(smoothness)
                        #print "smoothnes: " + str(smoothness)

                        if smoothness < agent.smoothness_ranges[0]:
                            smoothness = "low"
                        elif smoothness >= agent.smoothness_ranges[0] and smoothness < agent.smoothness_ranges[1]:
                            smoothness = "mid"
                        elif smoothness >= agent.smoothness_ranges[1]:
                            smoothness = "high"
                    else:
                        print "smoothness discard 1"
                        # Discard
                        #pass
                        continue
                except:
                    print "smoothness discard 2"
                    # Discard
                    #pass
                    continue

                        #print "static L: " + str(data_L)
                        #print "static R: " + str(data_R)
                                         

                gesture_new = gesture(data_L, data_R, centroid, energy, smoothness, 0, 0, 'sustain', agent.agent_num)
                gestureList.append(gesture_new)

    #print "gestures sustain: " + str(gestures_sustain)

    ### Normal gestures - left hand begins ####
    x = range(numpy.size(window_L))
    max, min = peakdetect(window_L, x, lookahead = 2)
    maxidx = [p[0] for p in max]
    minidx = [p[0] for p in min]    
    
    #print "maxidx: " + str(maxidx)
    #print "minidx: " + str(minidx)
    #print "Static start: " + str(static_start)+ " Static end: " + str(static_end)


    for i in xrange(numpy.size(minidx)):
        for k in xrange(numpy.size(static_start)):
            if minidx[i] == static_start[k]:
                minidx[i] = -1
    minidx = sorted(x for x in minidx if x > 0)    

    #print "mindix: " + str(minidx)

    starting_points = numpy.unique(static_end + minidx)
    ending_points = numpy.unique(static_start + minidx)
    ending_points = numpy.append(ending_points, (numpy.size(window_L)-1))
   
    #print "STARTING: " + str(starting_points)
    #print "ENDING: "  + str(ending_points)

    for i in xrange(numpy.size(starting_points)):
        starting_point = starting_points[i]
        ending_point = sorted(x for x in ending_points if x > starting_point)
        if numpy.size(ending_point) > 0:
            ending_point = ending_point[0]
            gestures.append([starting_point, ending_point])

            #gesture_L = window_L[starting_point:ending_point]
            #print "Gesture: #" + str(i) + ": "+ str(gesture_L)
      
    ###
    # Yhdista vierekkaiset lyhyet gesturet
    #print "before: " + str(gestures)
    gestures = combineShortGestures(gestures)
    #print "after: " + str(gestures)    
    #
    ###
    
    ###
    # Kokoa gesturet
    #print "Gestures: " + str(gestures)
    len_g = len(gestures)
    #print "len gestures " + str(len_g)

    for i in xrange(len_g):
        L_start = gestures[i][0]
        L_end = gestures[i][1]
        R_start = gestures[i][0]
        #print "i: " + str(i)

        # Jos viimeinen gesture
        if i == len(gestures)-1:
            if gestures[i][1] + sample_tail > numpy.size(window_R):
                R_end = numpy.size(window_R) # vasen vika + 150 tai ikkunan viimeinen indeksi
            else:
                R_end = gestures[i][1] + sample_tail
        
        # Jos ei viimeinen gesture
        else:
            #print "EI VIKA"
            #print "i: " + str(len_g)
            # Jos perakkaisten gestureiden vali >= 1.5s niin o_loppu = v_loppu + 150
            # Muutoin o_loppu = v_loppu
            if gestures[i+1][0] - gestures[i][1] > sample_tail:
                R_end = gestures[i][1] + sample_tail
            else:
                R_end = gestures[i+1][0]
        
        if R_end < gestures[i][1]:
            R_end = gestures[i][1]

        #print "Vasen kasi: " + str(L_start) + " " + str(L_end)
        #print "Oikea kasi: " + str(R_start) + " " + str(R_end)
        #print "---"
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
                # If no centroid detected - discard the gesture
                #pass
                continue               
        except:
            # If no centroid detected - discard the gesture
            #pass
            continue

        try:
            energy = agent.energy[R_start:R_end]

            if numpy.size(energy) > 0:
                #print "ENEG: " + str(energy)
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
                # Discard
                #pass
                continue
        except:
            # Discard
            #pass
            continue

        try:
            smoothness = agent.smoothness[R_start:R_end]
            #print "smoothness orig: " + str(smoothness)
            #smoothness = filter(lambda x: x != 0, smoothness)
            if numpy.size(smoothness) > 0:
                smoothness = numpy.mean(smoothness)
                #print "smoothnes: " + str(smoothness)

                if smoothness < agent.smoothness_ranges[0]:
                    smoothness = "low"
                elif smoothness >= agent.smoothness_ranges[0] and smoothness < agent.smoothness_ranges[1]:
                    smoothness = "mid"
                elif smoothness >= agent.smoothness_ranges[1]:
                    smoothness = "high"
            else:
                # Discard
                #pass
                continue
        except:
            # Discard
            #pass
            continue

        #try:
        #    irregularity = agent.irregularity[R_start:R_end]
        #    irregularity = filter(lambda x: numpy.isnan(x)== 0, irregularity)
        #    if numpy.size(irregularity) > 0:
        #        irregularity = numpy.mean(irregularity)
        #except:
        #    irregularity = 0

        #try:
            
        #    flatness = agent.flatness[R_start:R_end]
        #    #print "FLATNESS orig:" + str(flatness)
            
        #    flatness = filter(lambda x: numpy.isnan(x)==0, flatness)
        #    #print "FLATNESS filt:" + str(flatness)
        #    if numpy.size(flatness) > 0:
        #        flatness = numpy.mean(flatness)
        #        #print "FLATNESS mean :" + str(flatness)
        #except:
        #    flatness = 0

### 
    
        data_L = window_L[L_start:L_end]
        data_R = window_R[R_start:R_end]

        #gestureList = addGesture(gestureList, agent, L_start, R_end, R_start, R_end, 'normal')

        if numpy.size(data_L) > gesture_min_length:

            #gesture_new = gesture(data_L, data_R, centroid, energy, smoothness, irregularity, flatness, 'normal', agent)
            gesture_new = gesture(data_L, data_R, centroid, energy, smoothness, 0, 0, 'normal', agent.agent_num)

            gestureList.append(gesture_new)
        
    return gestureList
