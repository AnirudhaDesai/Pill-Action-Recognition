#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 10:34:59 2018

@author: anirudha
"""

import numpy as np

path = '../data/all_data.npy'
sensorData = np.asarray(np.load(path))
'''
sensorData has the following dimensions 
0 - Id -> Number
1 - Sensors -> 0 - Base, 1 - Cap, 2 - wearable
2 - Action -> 0 - Knock, 1 - Twist, 2 - Dispense, 3 - pill2Mouth, 4 - water2Mouth
3 - SensorType -> 0 - Accelerometer, 1 - Gyroscope
4 - Axis -> 0 -> x, 1->y, 2-z

'''
from datetime import datetime

def getUTCTimeDelta():
    return (datetime.utcnow() - datetime(1970,1,1)).total_seconds()
print (getUTCTimeDelta())



#def getBaseSensorData(rawData,axis):
#    '''
#    i/p -> 5d numpy array. 
#    o/p -> returns base sensors data for the given axis.
#    '''
#    if (axis == 0):
#        return rawData[:,0,:,:,0]
#    elif (axis == 1):
#        return rawData[:,0,:,:,1]
#    elif (axis == 2):
#        return rawData[:,0,:,:,2]
#    else :
#        return rawData[:,0,:,:,:]
#
#def getCapSensorData(rawData):
#    return rawData[:,1]
#
#def getWearableSensorData(rawData):
#    return rawData[:,2]
#



    
    
    
    


