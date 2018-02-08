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
 
path = 'test_bed/'
csv = {}
sensors = ['base_accel_csv', 'base_gyro_csv', 
          'cap_accel_csv', 'cap_gyro_csv',
          'wear_accel_csv', 'wear_gyro_csv', ]

print('Reading CSVs..')
csv[sensors[0]] = np.genfromtxt(path + 'METAWEAR_base_sensor_accel.csv', delimiter=',')
csv[sensors[1]] = np.genfromtxt(path + 'METAWEAR_base_sensor_gyro.csv', delimiter=',')

csv[sensors[2]] = np.genfromtxt(path + 'METAWEAR_cap_sensor_accel.csv', delimiter=',')
csv[sensors[3]] = np.genfromtxt(path + 'METAWEAR_cap_sensor_gyro.csv', delimiter=',')

csv[sensors[4]] = np.genfromtxt(path + 'WEARABLE_sensor_accel.csv', delimiter=',')
csv[sensors[5]] =  np.genfromtxt(path + 'WEARABLE_sensor_gyro.csv', delimiter=',')

actions = np.array(pd.read_csv(path + 'actions.csv'))
act_st = actions[:, 1::2]
act_end = actions[:, 2::2]

vid_st = np.genfromtxt(path + 'sync.csv')
vid_st = vid_st[:, 1]
print('Done Reading')

cur_idx = [0 for i in range(len(sensors))]

data = [
        [
         [ 
          [
           [
            [
             0
            ]*(e%3) for e in range(3)      # Dimensions(X,Y,Z)
           ] for d in range(2)             # Sensor_Types
          ] for c in range(len(act_st[0])) # Actions
         ] for b in range(len(sensors)//2) # Sensors
        ] for a in range(actions.shape[0]) # Ids
       ]
data = np.array(data)
rows = np.array(data[:]) # For Debugging Purposes

print('Cleaning Data...')

for idx in range(actions.shape[0]):
    for sensor in range(len(sensors)):
        actst = 0
        actend = 0
        for action in range(len(act_st[idx])):
            s_name = sensors[sensor]
            s_idx = sensor//2
            sensor_t = sensor%2
            
            actst = findtim(csv[s_name][:,0], cur_idx[sensor], vid_st[idx] + getms(act_st[idx, action]))
            actend = findtim(csv[s_name][:,0], cur_idx[sensor], vid_st[idx] + getms(act_end[idx, action]))
            
            #print(csv[s_name][actst:actend+1, 1].dtype)
            rows[idx, s_idx, action, sensor_t, 0] = np.arange(actst, actend+1)
            rows[idx, s_idx, action, sensor_t, 1] = np.arange(actst, actend+1)
            rows[idx, s_idx, action, sensor_t, 2] = np.arange(actst, actend+1)
            
            data[idx, s_idx, action, sensor_t, 0] = csv[s_name][actst:actend+1, 1]
            data[idx, s_idx, action, sensor_t, 1] = csv[s_name][actst:actend+1, 2]
            data[idx, s_idx, action, sensor_t, 2] = csv[s_name][actst:actend+1, 3]
        cur_idx[sensor] = actend
        
print('Data Cleaned - Data Size ->' + str(data.shape))
print('Saving all data...')        
np.save('all_data.npy', data)


