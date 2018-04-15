# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 10:34:21 2018

@author: amitrc
"""

'''
This is a service class. No need to make
objects, all methods to be kept static.

'''
import threading

class Q_service:
    
    # This method is here but do not use.
    def __init__(self):
        pass
    
    @staticmethod
    def enqueue(data, 
                tims, 
                medicine_id,
                user_id):
        '''
        Enqueue data pertaining to supplied medicine_id
        params:
            data: All data as 3-D array of lists - [device_type, s_type, axis]
            tims: All timestamps for data 2-D array of lists [device_type, s_type]
            medicine_id: Integer medicine Id unique across users
            
            Note that there are only 2 device types - 0-> wearable, 1->metawear
        '''
        print('Executing Q_service on thread', threading.current_thread())
    
    @staticmethod
    def dispatch():
        pass
    