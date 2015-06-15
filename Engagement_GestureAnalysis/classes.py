import numpy
from dataCollectors import *

class engagementData:
    def __init__(self):
        self.global_max = 0
        self.global_min = 127
        self.buffer = numpy.zeros(0)
        self.third = numpy.zeros(0)
        self.trend = numpy.zeros(0)
        self.meanValues = numpy.zeros(0)
        self.meanValuesNormalized = numpy.zeros(0)


    def calculate(eng, lipCornerDepressorLeft, handTipLeft_duration, spineShoulder_acc, leanY, activity, neck_acc, wristRight_duration, head_acc, shoulderRight_acc):
        eng = 83.145 + -4.762 * lipCornerDepressorLeft + 4.4851 * handTipLeft_duration + -0.18154 * spineShoulder_acc + 10.479 * leanY + -0.019883 * activity + -0.48392 * neck_acc + 1.4508 * wristRight_duration + -0.18123 * head_acc + -0.22347 * shoulderRight_acc
        eng = numpy.max([0, numpy.min([127, eng])])
        return eng

class musicalSpace:
    def __init__(self):
        self.centroid = [0, 0, 0]
        self.smoothness = [0, 0, 0]
        self.energy = [0, 0, 0]

class gesture:
    def __init__(self, data_L, data_R, centroid, energy, smoothness, engagement, emg, type, agent_num):
        self.data_L = data_L
        self.data_R = data_R
        self.engagement = 0
        self.last_play = numpy.inf
        self.n_plays = 0
        self.scale_L = 0
        self.scale_R = 0

        # Sound features:
        self.smoothness = smoothness
        self.centroid = centroid
        self.energy = energy
        self.engagement = engagement
        self.emg = emg

        # Other data
        self.type = type
        self.agent_num = agent_num
        

# Animation Unit (AU) coefficients. These describe the facial features.
class facialFeatures:
    def __init__(self):
        self.leftEyeClosed, self.rightEyeClosed, self.leftEyebrowLowerer, self.rightEyebrowLowerer = 0, 0, 0, 0
        self.jawOpen, self.jawSlideRight, self.leftCheekPuff, self.rightCheekPuff = 0, 0, 0, 0
        self.lipCornerDepressorLeft, self.lipCornerDepressorRight, self.lipPucker, self.lipStretcherLeft, self.lipStretcherRight, self.lowerLipDepressorLeft, self.lowerLipDepressorRight, self.lipCornerPullerLeft, self.lipCornerPullerRight = 0, 0, 0, 0, 0, 0, 0, 0, 0

# Body orientations
class bodyOrientations:
    def __init__(self):
        self.leanX, self.leanY = 0, 0
        self.headPitch, self.headYaw, self.headRoll = 0, 0, 0

class faceOrientations:
    def __init__(self):
        self.pointOfInterest = 0
        self.instrument_1 = 0
        self.instrument_2 = 0
        self.instrument_3 = 0
        self.audience = 0

class faceTrackers:
    def __init__(self):
        self.state = 0

class movements:
    def __init__(self):
        self.motion = 0
    def plusMotion(self):
        self.motion = self.motion + 1
    def minusMotion(self):
        self.motion = self.motion - 1
    def returnMotion(self):
        if (self.motion > 0):
            return True
        if (self.motion == 0):
            return False

class handProximities:
    def __init__(self):
        self.rightProximity = 0
        self.leftProximity = 0    
        self.rightPrevProximity = 0
        self.leftPrevProximity = 0


class joints:
        def __init__(self, name):
            self.x, self.y, self.z = 0, 0, 0
            self.velX, self.velY, self.velZ = 0, 0, 0 
            self.accX, self.accY, self.accZ, self.acc = 0, 0, 0, 0
            self.tic, self.moveStartTic, self.moveStopTic, self.proximityTic = 0, 0, 0, 0
            self.moveState = 0
            self.flowVector = 0
            self.duration = 0
            self.proximity = 0
            self.name = name

        def setPos(joint, x, y, z, tic, velX, velY, velZ, accX, accY, accZ, acc):
            joint.x, joint.y, joint.z, joint.tic, joint.velX, joint.velY, joint.velZ, joint.accX, joint.accY, joint.accZ, joint.acc = x, y, z, tic, velX, velY, velZ, accX, accY, accZ, acc
            jointPosAccCollector(joint)

        def returnPos(joint):
            return joint.x, joint.y, joint.z, joint.tic, joint.velX, joint.velY, joint.velZ
        
        def startMove(joint):
            joint.moveState, joint.moveStartTic = 1, time.time()

        def stopMove(joint, duration):
            joint.moveState, joint.moveStopTic = 0, time.time()
            joint.duration = duration
            jointMovementDurationCollector(joint)

        def returnMove(joint):
            return joint.moveState, joint.moveStartTic

        def calcAcc(joint, x, y, z):
                [x_prev, y_prev, z_prev, time_prev, velX_prev, velY_prev, velZ_prev] = joint.returnPos()
                deltaTime = time.time()-time_prev
                deltaPosX = x - x_prev
                deltaPosY = y - y_prev
                deltaPosZ = z - z_prev
                velX = deltaPosX / deltaTime
                velY = deltaPosY / deltaTime
                velZ = deltaPosZ / deltaTime              
                deltaVelX = velX - velX_prev
                deltaVelY = velY - velY_prev
                deltaVelZ = velZ - velZ_prev

                # Acceleration measurement:
                accX = numpy.abs(deltaVelX / deltaTime)
                accY = numpy.abs(deltaVelY / deltaTime)
                accZ = numpy.abs(deltaVelZ / deltaTime)

                interval = time.time()-joint.moveStopTic

                if accX < 60 and accY < 60 and accZ < 60:
                    acc = [accX, accY, accZ]
                    acc = numpy.linalg.norm(acc)
                    joint.setPos(x, y, z, time.time(), velX, velY, velZ, accX, accY, accZ, acc)

                    if joint.name == 'handTipLeft':
                        offset_threshold = 2
                    else:
                        offset_threshold = 1

                    if (acc > 3 and joint.moveState == 0 and interval > 0.5):
                        joint.startMove()
                        movement.plusMotion()
                    
                    elif (acc < offset_threshold and joint.moveState == 1):
                        duration = time.time() - joint.moveStartTic
                        joint.stopMove(duration)
                        movement.minusMotion()
               
                    return acc
                else:
                    return 0

class agent_data:
    def __init__(self, agent_num):
        self.agent_num = agent_num
        self.values_L = []
        self.values_R = []
        
        self.centroid = []
        self.centroid_mus = []
        self.energy = []
        self.energy_mus = []
        self.smoothness = []
        self.smoothness_mus = []

        self.myodyn = []

        self.current_L = 0;
        self.current_R = 0;
        self.prevMove = []
        self.manual = 0
        self.prev_energy = "off"
        self.device_state = 1     
        self.engagement = []
        self.emg = []

        if agent_num == 1:
            self.centroid_ranges = [7000., 10000.]
            #self.smoothness_ranges = [-0.3, 0.3]
            self.smoothness_ranges = [-0.946, 0.308]
            self.energy_ranges = [90., 125.]
            self.energy_low = 65
            self.energy_high = 80

        if agent_num == 2:
            self.centroid_ranges = [7000, 9000]
            #self.smoothness_ranges = [-2.5, -1.5]
            self.smoothness_ranges = [-1.65, -0.68]
            self.energy_ranges = [110., 125.]
            self.energy_low = 60
            self.energy_high = 90

        if agent_num == 3:
            self.centroid_ranges = [3500., 4500.]
            #self.smoothness_ranges = [-2.5, -2.2]
            self.smoothness_ranges = [-2.25, -1.88]
            self.energy_ranges = [120., 132.]
            self.energy_low = 60
            self.energy_high = 80