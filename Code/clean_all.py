# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 09:51:10 2018

@author: amitrc
"""

import numpy as np
import pandas as pd

def getms(st):
    m = int(st[:st.find(':')])
    ms = int(float(st[st.find(':')+1:])*1000)
    return m*60*1000 + ms

def findtim(arr, st_idx, target):
    for i in range(st_idx, len(arr)):
        if arr[i] >= target:
            return i
 

path = '../misc/test_bed_all/'

csv = {}
sensors = ['base_accel_csv', 'base_gyro_csv', 
          'cap_accel_csv', 'cap_gyro_csv',
          'wear_accel_csv', 'wear_gyro_csv', ]

buffer = 0# Quantized jumps depending on sampling frequency
bufferSize = 5# Number of samples per buffer jump
CORRECT_FOR_SENSORS = True

print('Reading CSVs..')
csv[sensors[0]] = np.genfromtxt(path + 'METAWEAR_base_sensor_accel.csv', delimiter=',')
csv[sensors[1]] = np.genfromtxt(path + 'METAWEAR_base_sensor_gyro.csv', delimiter=',')

csv[sensors[2]] = np.genfromtxt(path + 'METAWEAR_cap_sensor_accel.csv', delimiter=',')
csv[sensors[3]] = np.genfromtxt(path + 'METAWEAR_cap_sensor_gyro.csv', delimiter=',')

csv[sensors[4]] = np.genfromtxt(path + 'WEARABLE_sensor_accel.csv', delimiter=',')
csv[sensors[5]] =  np.genfromtxt(path + 'WEARABLE_sensor_gyro.csv', delimiter=',')

if CORRECT_FOR_SENSORS == True:
    csv[sensors[0]][:270299, 3] = -csv[sensors[0]][:270299, 3] # correct base accel
    print('Mean base accel Z-axis = ', np.mean(csv[sensors[0]][:, 3]))
    #csv[sensors[2]][:274397, 3] = -csv[sensors[2]][:274397, 3]
    print('Mean cap accel Z-axis = ', np.mean(csv[sensors[2]][:, 3]))

actions = np.array(pd.read_csv(path + 'actions.csv'))
act_st = actions[:, 1::2]
act_end = actions[:, 2::2]

vid_st = np.genfromtxt(path + 'sync.csv', delimiter=',')
vid_st = vid_st[:, 1]
print('Done Reading')

cur_idx = [0 for i in range(len(sensors))]

num_actions = act_st.shape[1]
num_samples = actions.shape[0]
data = np.zeros((num_samples*num_actions*(buffer+1), 3, 2, 3), dtype = np.object)
#rows = np.array(data[:]) # For Debugging Purposes
keys = np.zeros((num_samples*num_actions*(buffer+1)))


print('Cleaning Data...')

for idx in range(num_samples):
    for sensor in range(len(sensors)):
        actst = 0
        actend = 0
        for action in range(num_actions):
            s_name = sensors[sensor]
            s_idx = sensor//2
            sensor_t = sensor%2
            
            actst = findtim(csv[s_name][:,0], cur_idx[sensor], vid_st[idx] + getms(act_st[idx, action]))
            actend = findtim(csv[s_name][:,0], cur_idx[sensor], vid_st[idx] + getms(act_end[idx, action]))
            
            for buf in range(buffer + 1):
                start = actst-(buffer-buf)*bufferSize
                end = actend + 1 + buf*bufferSize
                curIdx = idx*(buffer+1)*num_actions + action*(buffer+1) + buf
                if curIdx == 24 and s_idx == 1 and sensor_t == 0:
                    print(cur_idx[sensor] , vid_st[idx], vid_st[idx] + getms(act_st[idx, action]), act_st[idx, action]) 
                data[curIdx, s_idx, sensor_t, 0] = csv[s_name][start:end, 1]
                data[curIdx, s_idx, sensor_t, 1] = csv[s_name][start:end, 2]
                data[curIdx, s_idx, sensor_t, 2] = csv[s_name][start:end, 3]
                keys[curIdx] = action
        cur_idx[sensor] = actend
        
        
print('Data Cleaned - Data Size ->' + str(data.shape))
print('Labels Size ->' + str(keys.shape))
print('Saving all data...')        

np.savez(path + 'combined_data.npz', data, keys)

