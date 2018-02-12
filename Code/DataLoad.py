#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 10:52:41 2018

@author: anirudha
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, freqs
import numpy as np
import FeatureExtractorUtils as fe
import scipy

data = pd.read_csv('../METAWEAR_cap_sensor_accel.csv')
data = data.iloc[:,0:4]
data = data.values

dataTime = data[:, 0]
dataX, dataY, dataZ = data[:,1], data[:,2], data[:,3]

plt.figure(1)
plt.clf()   
b, a = butter(3, 0.3, 'low' , analog = 'True')
w, h = freqs(b, a, worN=2000)
plt.plot((100 * 0.5 / np.pi) * w, abs(h), label="order = %d" % 3)

plt.figure(2)
plt.clf()
#plt.plot(dataTime[20000:30000], dataY[20000:30000], label = 'Noisy signal')

y = lfilter(b,a, dataY[20000:30000])

#plt.plot(dataTime[20000:30000], y, label = 'Filtered Signal')
#
#b, a = butter(9, 0.3, 'high' , analog = 'True')
#yhigh = lfilter(b,a, dataY[20000:])
#    
#plt.plot(dataTime[20000:], yhigh, label = 'body Signal')
#plt.show()
#
#plt.figure(3)
#gComp = fe.getBodyAccelComponent(dataY[20000:])
#plt.plot(dataTime[20000:], gComp, label = 'Filtered Signal')
#plt.show()

plt.figure(4)
sig = dataX[20000:]
time = dataTime[20000:]
plt.plot(time, sig , label = 'Signal')
freqSig = np.fft.rfft(sig)
print (freqSig)
mag = np.abs(freqSig)
print (mag, mag.shape)
print (np.argmax(mag))
print ('average', np.average(mag))
print (scipy.stats.skew(mag))
print (scipy.stats.skew(mag, bias = False))
phase = np.angle(freqSig)
plt.figure(5)
plt.plot( mag , label = 'fft')
plt.show()
plt.plot( freqSig , label = 'fft')
plt.show()
plt.figure(6)
plt.plot(range(len(phase)), phase , label = 'phase')
#ifft
invSig = np.fft.irfft(freqSig)
plt.figure(7)
plt.plot(range(len(invSig)), invSig , label = 'inverse fft')
plt.show()