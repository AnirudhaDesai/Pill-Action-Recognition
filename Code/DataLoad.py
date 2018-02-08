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

b, a = butter(9, 0.3, 'high' , analog = 'True')
yhigh = lfilter(b,a, dataY[20000:])
    
plt.plot(dataTime[20000:], yhigh, label = 'body Signal')
plt.show()

plt.figure(3)
gComp = fe.getBodyAccelComponent(dataY[20000:])
plt.plot(dataTime[20000:], gComp, label = 'Filtered Signal')
plt.show()