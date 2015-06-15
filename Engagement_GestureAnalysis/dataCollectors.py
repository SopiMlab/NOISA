import time
import numpy

rehearsal = 0

# Data stream collectors

# Collects point of interest on a regular sampling interval
def pointOfInterestCollector(faceOrientation, faceTracker):
    if rehearsal == 0:
        filename = 'face_orientation.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        if (faceTracker.state == 1):
            file.write("PointOfInterest: " + str(faceOrientation.pointOfInterest) + " Instrument_1: " + str(faceOrientation.instrument_1) + " Instrument_2: "+ str(faceOrientation.instrument_2) + " Instrument_3: "+ str(faceOrientation.instrument_3) + " Audience: "+ str(faceOrientation.audience) + '\n')
        else:
            file.write("PointOfInterest: face lost \n")
        file.close()


# Collects raw face data (expression data) on a regular sampling interval
def faceDataCollector(facialFeature, faceTracker):
    if rehearsal == 0:
        filename = 'face_raw.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " FaceTrackerState: " + str(faceTracker.state) + " ")
        if (faceTracker.state == 1):
            file.write("jawOpen: " + str(facialFeature.jawOpen) + " ")
            file.write("jawSlideRight: " + str(facialFeature.jawSlideRight) + " ")
            file.write("leftCheekPuff: " + str(facialFeature.leftCheekPuff) + " ")
            file.write("rightCheekPuff: " + str(facialFeature.rightCheekPuff) + " ")
            file.write("lipCornerDepressorLeft: " + str(facialFeature.lipCornerDepressorLeft) + " ")
            file.write("lipCornerDepressorRight: " + str(facialFeature.lipCornerDepressorRight) + " ")
            file.write("lipCornerPullerLeft: " + str(facialFeature.lipCornerPullerLeft) + " ")
            file.write("lipCornerPullerRight: " + str(facialFeature.lipCornerPullerRight) + " ")
            file.write("lipStretcherLeft: " + str(facialFeature.lipStretcherLeft) + " ")
            file.write("lipStretcherRight: " + str(facialFeature.lipStretcherRight) + " ")
            file.write("lowerLipDepressorLeft: " + str(facialFeature.lowerLipDepressorLeft) + " ")
            file.write("lowerLipDepressorRight: " + str(facialFeature.lowerLipDepressorRight) + " ")
            file.write("lipPucker: " + str(facialFeature.lipPucker) + " ")
            file.write("leftEyeClosed: " + str(facialFeature.leftEyeClosed) + " ")
            file.write("rightEyeClosed: " + str(facialFeature.rightEyeClosed) + " ")
            file.write("leftEyebrowLowerer: " + str(facialFeature.leftEyebrowLowerer) + " ")
            file.write("rightEyebrowLowerer: " + str(facialFeature.rightEyebrowLowerer))
        file.write('\n')
        file.close()



def trunkLeanCollector(bodyOrientation):
    if rehearsal == 0:
        filename = 'trunkLean.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        file.write("leanX: " + str(bodyOrientation.leanX) + " ")
        file.write("leanY: " + str(bodyOrientation.leanY) + '\n')
        file.close()


def automationCollector(agentNum, size_L):
    if rehearsal == 0:
        filename = 'automation.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        file.write("Agent: " + str(agentNum) + " " + str(size_L) +  '\n')
        file.close()


def headOrientationCollector(bodyOrientation):
    if rehearsal == 0:
        filename = 'headOrientation.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        file.write("headPitch: " + str(bodyOrientation.headPitch) + " ")
        file.write("headYaw: " + str(bodyOrientation.headYaw) + " ")
        file.write("headRoll: " + str(bodyOrientation.headRoll) + '\n')  
        file.close()


def handProximityCollector(hand, target):
    if rehearsal == 0:
        filename = 'handProximity.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        file.write(hand + " " + target + '\n')
        file.close()

def bodycenterPosCollector(spineMid):
    if rehearsal == 0:
        filename = 'bodyPositions.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        file.write(str(spineMid.x) + " " + str(spineMid.y) + " " + str(spineMid.z)  + '\n') 
        file.close()

def asyncMovementCollector(movement, jointVector, controlInput):
    if rehearsal == 0:
        filename = 'async_movement.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        jointString = ""
        jointNum = numpy.size(jointVector)
        if (movement.returnMotion() == True):
            for i in xrange(jointNum):
                try:
                    if (jointVector[i].moveState == 1):
                        jointString = jointString + " " + jointVector[i].name
                except:
                    pass
            mov = "true: " + str(movement.motion) + " " + jointString
        else:
            mov = "false"
        if (controlInput.touch == 1):
            touch = "true"
        else:
            touch = "false"
        file.write("Movement: " + mov + " Touch: " + touch + '\n')
        file.close()


def jointMovementDurationCollector(joint):
    if (rehearsal == 0):
        filename = 'jointMoveDurations.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        stopTime = time.time()
        startTime = stopTime - joint.duration   
        file.write(str(joint.name) + " Start: " + str(startTime) + " Stop: " +  str(stopTime) + " Duration : " + str(joint.duration) + '\n' )
        file.close()

def jointPosAccCollector(joint):
    if (rehearsal == 0):
        filename = 'joint_pos_acc.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")       
        file.write(joint.name  + " X: " + str(joint.x) + " Y: " + str(joint.y) + " Z: " + str(joint.z) + " velX: " + str(joint.velX) + " velY: " + str(joint.velY) + " velZ: " + str(joint.velZ) + " accX: " + str(joint.accX) + " accY: " + str(joint.accY) + " accZ: " + str(joint.accZ) + " acc: "  + str(joint.acc) + '\n')   
        file.close()

def totalAccCollector(totalAcceleration):
    if (rehearsal == 0):
        filename = 'body_totalAcc.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        file.write(str(totalAcceleration) + '\n')
        file.close() 

def engagementCollector(engagement):
    if (rehearsal == 0):
        filename = 'predictedEngagement.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")   
        file.write("Engagement: " + str(engagement) + '\n') 
        file.close()


def faceStateCollector(state):
    if (rehearsal == 0):
        filename = 'faceState.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")   
        file.write("State: " + str(state) + '\n')   
        file.close()


def agentCollector(instrument, controller, value):
    if (rehearsal == 0):
        filename = 'agent_' + str(instrument) + '_data.txt'
        file = open(filename, 'a')
        file.write("Time: " + str(time.time()) + " ")
        file.write(controller + " " + str(value) + '\n')
        file.close


