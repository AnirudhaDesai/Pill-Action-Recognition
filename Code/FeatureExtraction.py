# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import scipy
from scipy import signal

class FeatureExtraction(object, data, samplingFreq=25):
    ''' Feature Extraction class 
        Inputs :
            data : 6-d array with each dimension being 
                0 - id, 1- Sensor, 2 -Action, 3- SensorType, 4 - axis, 5 - time
            samplingFreq - sampling frequency of the sensor
    '''            
    
    self.samplingFreq = samplingFreq
    
    self.data = data
    
    def removeNoise(self, signal):
        # median filtering 
        signalMedianFiltered = scipy.signal.medfilt(signal)
        
        # 3rd order butterworth filter with corner frequency = cornerFreq
        # corner Frequency is set to be 0.4 times the sampling frequency
        num, den = signal.butter(3, self.samplingFreq*0.4, 'low')
        signalOut = scipy.signal.filtfilt(num,den, signal)
        
        return signalOut

        
        
        
    
    