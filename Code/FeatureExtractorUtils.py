#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 10:35:29 2018

@author: anirudha
"""
import scipy
from scipy.signal import butter, lfilter, freqs
import numpy as np
from statsmodels import robust
from scipy.stats import iqr


def getGravityAccelComponent(data, cornerFreq = 0.3, order = 3):
    ''' ip -> data (numpy array like), corner Frequency and order of butter
            worth filter
        o/p - Applies low pass butterworth filter on data and returns gravity
        component
        '''
    b,a = butter(order, cornerFreq, 'low' , analog = 'True')
    gComponent = lfilter(b,a, data)
    return gComponent
    
def getBodyAccelComponent(data, cornerFreq = 0.3, order = 9):
    b, a = butter(order, cornerFreq, 'high' , analog = 'True')
    bodyComponent = lfilter(b,a, data)
    return bodyComponent

def getMean(data):
    return np.mean(data)

def getStdDev(data):
    return np.std(data)

def getMeadianAbsDev(data):
    return robust.mad(data)
def getMax(data):
    return np.amax(data)
def getMin(data):
    return np.amin(data)
def getSMA(data):
    '''
    i/p - data is a 2D array of size (4,N). 0->x, 1->y, 2->z, 3->t
    o/p - returns the signal magnitude area. Refer Wiki for details.
    '''
    N = data.shape[1]
    prevTime = data[3,0]
    curX,curY,curZ = data[0,0], data[1,0],data[2,0]
    sma = 0
    for i in range(1,N):
        dt = data[3,i] - prevTime
        # take vector magnitude
        mag = np.sqrt(curX**2 + curY**2 + curZ**2)
        sma += mag*dt
        prevTime = data[3,i]
        curX, curY, curZ = data[0,i], data[1,i], data[2,i]
    
    return sma

def getEnergyMeasure(data):
    '''
    i/p - data is a 2D array of size (3,N). 0-x, 1-y,2-z
    o/p - Energy measure of the data along each axis. Energy measure
            is taken to be the mean of squares along each axis
    '''        
    return np.mean(data[0]**2), np.mean(data[1]**2), np.mean(data[2]**2)

def getIQR(data):
    '''
    i/p - data is a 2D or a 1d array. 
    o/p - returns the Interquartile range along every dimension. Assumes 
            the x, y and z axes along axis = 1. Basically, the i/p as (3,N)
    '''
    if(data.ndim == 2):
        return iqr(data, axis = 1)
    else:
        return iqr(data)
    
def getEntropy(data):
    ''' May need to edit this function. May not be the right way to calculate
    entropy of the time signal"
    '''
    return scipy.stats.entropy(data)
def getFFT(data):
    ''' i/p  : time domain data
        o/p :  Frequency domain info. Performs fft on time series data.
    '''
    return np.fft.rfft(data)
def getMaxInds(fData):
    '''
    ip : frequency domain signal. Typically the output of getFFT(data)
    op : Maximum index of the frequency component
    '''
    mag = np.abs(fData)
    return np.argmax(mag)

def getMeanFreq(fData):
    
    return np.average(fData)

def getSkewness(fData):
    ''' 
    ip : frequency domain signal. Typically the output of getFFT(data)
    op : skewness of the frequency distribution
    '''
    return scipy.stats.skew(fData, bias = False)

def getKurtosis(fData):
    ''' 
    ip : frequency domain signal. Typically the output of getFFT(data)
    op : skewness of the frequency distribution
    '''
    return scipy.stats.kurtosis(fData, bias = False)