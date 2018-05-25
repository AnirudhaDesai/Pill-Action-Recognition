# -*- coding: utf-8 -*-
"""
Created on Tue May 15 15:48:16 2018

@author: amitrc
"""

import requests
import numpy as np
import time
from datetime import datetime, timedelta
from hashlib import sha256 as sha2

TEST_EMAIL = 'test@gmail.com'
TEST_INSTALL_ID = 'b5eee207-c0e0-45f0-b3fd-913283ed2h9e'
TEST_PUSH_ID = 'c6REjdP-bE8:APA91bHooY8ng4gTfyN-xvBwgDBsSnSqvlVcEGsewME9M2649iFkDTGSgn7YTr_FyuKbRxVTGLa81eGPhV6LYvpBJZX6ODM6-LGFSUox0z3WI-yMWyBP-zp2UQ7EKrnhvqVpZPNk1ODF'
TEST_PATIENT_ID = '1728452'
TEST_TIMES = [11, 15, 10, 13, 18]
TEST_DAYS_TO_GEN = 31
TEST_DATA_BATCH_LENGTH = 5 # in seconds
TEST_DATA_RATE = 40 # in milliseconds
TEST_MAC_ADDRESS = 'CA:95:82:BC:73:0A'
MED_IDS = []


base_url = 'http://localhost:5000'
register_endpoint = '/register_device'
create_user_endpoint = '/create_user'
get_med_data_endpoint = '/get_medicine_data'
create_intake_endpoint = '/create_intake'
remove_user_endpoint = '/remove_user'
upload_sensor_readings_endpoint = '/upload_sensor_readings'


def generate_create_intake_data(tim):
    if tim.weekday() in [0, 2, 4]:
        num_intakes = 5
    else:
        num_intakes = 2
        
    intakes = []
    for i in range(num_intakes):
        intake_status = np.random.choice([0, 1, 2, 3])
        
        plan_hour = TEST_TIMES[i]
        planned_date_time = tim.replace(hour=plan_hour).isoformat()
        actual_date_time = None
        if intake_status == 0:
            actual_date_time = tim.replace(hour=plan_hour).isoformat()
        elif intake_status == 1:
            actual_date_time = tim.replace(hour=plan_hour-2).isoformat()
        elif intake_status == 2:
            actual_date_time = tim.replace(hour=plan_hour+2).isoformat()
        
        intakes.append({'medicine_id': MED_IDS[i], 
                        'planned_date_time': planned_date_time,
                        'actual_date_time': actual_date_time,
                        'intake_status': int(intake_status)})
    return intakes

def construct_reading(d_type, s_type, med_idx, data_list, tim):
    reading = str(d_type) + '`' + str(s_type) + '`' + str(MED_IDS[med_idx]) + '`' + TEST_MAC_ADDRESS + '`'
    if len(data_list) == 1:
        reading = reading + str(data_list[0]) + '`'
    else:
        xx, yy, zz = data_list
        reading = reading + str(xx)[:9] + '~' + str(yy)[:9] + '~' + str(zz)[:9] + '`'
    reading = reading + str(tim)
    return reading
 
def generate_sensor_readings(med_idx):
    tim = int(time.time()*1000)
    
    ret_data = []
    num_samples = (TEST_DATA_BATCH_LENGTH*1000)//TEST_DATA_RATE
    for i in range(num_samples):
        tim = tim + (i*TEST_DATA_RATE)
        for d_type in range(2):
            for s_type in range(3):
                cur_reading = ''
                if s_type == 2:
                    if d_type == 0:
                        continue
                    
                    touch = np.random.randint(0, 10) % 2
                    cur_reading = construct_reading(d_type, s_type, med_idx, [touch], tim)
                else:
                    data_list = np.random.randn(3)
                    cur_reading = construct_reading(d_type, s_type, med_idx, data_list, tim)
                ret_data.append(cur_reading)
    
    return ret_data

def test_register_device():
    url = base_url + register_endpoint
    
    alg = sha2()
    alg.update(TEST_EMAIL.encode())
    headers = {'User-Id': alg.hexdigest().upper(),
               'Install-Id': TEST_INSTALL_ID}
    response = requests.post(url, data={'push_id': TEST_PUSH_ID}, headers=headers)
    return response.text
    
    
def test_create_user():
    url = base_url + create_user_endpoint
    
    data = {'u_id': TEST_EMAIL, 'p_id': TEST_PATIENT_ID}
    data['med_name_1'] = 'Raltegravir'
    data['days1ALL'] = 'ON'
    data['times1time1'] = '11:00'
    data['times1time2'] = '15:00'
    data['med_name_2'] = 'Truvada'
    data['days2Monday'] = 'ON'
    data['days2Wednesday'] = 'ON'
    data['days2Friday'] = 'ON'
    data['times2time1'] = '10:00'
    data['times2time2'] = '13:00'
    data['times2time3'] = '18:00'
    
    response = requests.post(url, data=data)
    return response.text

def test_get_medicine_data():
    url = base_url + get_med_data_endpoint
    
    alg = sha2()
    alg.update(TEST_EMAIL.encode())
    headers = {'User-Id': alg.hexdigest().upper(), 'Install-Id': TEST_INSTALL_ID}
    
    response = requests.get(url, headers=headers)
    response = response.json()
    
    MED_IDS.append(response['medicines'][0]['id'])
    MED_IDS.append(response['medicines'][0]['id'])
    MED_IDS.append(response['medicines'][1]['id'])
    MED_IDS.append(response['medicines'][1]['id'])
    MED_IDS.append(response['medicines'][1]['id'])
    return response

def test_create_intake():
    tim = datetime.now()
    tim = tim.replace(hour=0, minute=0, second=0, microsecond=0)
    
    tim = tim - timedelta(days=TEST_DAYS_TO_GEN)
    
    intakes = []
    for i in range(TEST_DAYS_TO_GEN - 5):
        intakes.extend(generate_create_intake_data(tim + timedelta(days=i)))
    
    url = base_url + create_intake_endpoint
    
    for i in range(len(intakes)):
        response = requests.post(url, json=intakes[i])
        print(response.text)

def test_remove_user():
    url = base_url + remove_user_endpoint
    
    response = requests.post(url, data={'u_id': TEST_EMAIL})    
    return response.text


def test_upload_sensor_readings():
    url = base_url + upload_sensor_readings_endpoint
    
    alg = sha2()
    alg.update(TEST_EMAIL.encode())
    headers = {'User-Id': alg.hexdigest().upper()}
    sensor_readings = generate_sensor_readings(0)
    
    response = requests.post(url, json=sensor_readings, headers=headers)
    return response.text

tests = [test_register_device, 
         test_create_user, 
         test_get_medicine_data, 
         test_create_intake,
         test_upload_sensor_readings,
         test_remove_user]

if __name__ == '__main__':
    for test in tests:
        print(test())


