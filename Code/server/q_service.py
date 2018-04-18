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
from collections import defaultdict

class Q_service:
    helper = None
    pred_service = None
    med_data = defaultdict()
    med_timestamps = defaultdict()
    t_window = 10   
    slide_window = 1        #number of seconds to slide 
    # This method is here but do not use.
    def __init__(self, hp):
        pass
    @staticmethod
    def start_service(hp, pred_service):
        Q_service.helper = hp
        Q_service.pred_service = pred_service
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
        if medicine_id in Q_service.med_data:
            # append to list 
            D,S,A = Q_service.med_data[medicine_id].shape
            for d in D:
                for s in S:
                    for a in A:
                        Q_service.med_data[medicine_id][d,s,a].append(data[d,s,a])
                        Q_service.med_timestamps[d,s].append(tims[d,s])
        else:
            # new medicine_id to predict
            Q_service.med_data[medicine_id] = data.copy()
            Q_service.med_timestamps = tims.copy()
        # check if timestamp duration is sufficient for prediction. Using 0,0 for reference
        start,end =  Q_service.med_data[medicine_id][0,0][0,-1]
        if end-start>Q_service.t_window:
            Q_service.dispatch(medicine_id,user_id)

        print('Executing Q_service on thread', threading.current_thread())
    
    def dispatch(med_id, u_id):
        D,S,A = Q_service.med_data[med_id].shape
        total_data = Q_service.med_data[med_id]
        times = Q_service.med_timestamps[med_id]
        dispatch_data = Q_service.hp.get_clean_data_array((D,S,A))
        for d in D:
            for s in S:
                s_time = times[d,s,0][0]
                e_idx = 0      # index upto which data should be dispatched
                p_idx = -1     #index upto which data should be popped
                while(e_idx<len(times[d,s,0]) and times[d,s,0][e_idx]<s_time + Q_service.t_window):
                    e_idx += 1
                    if p_idx < 0 and times[d,s,0][e_idx]<s_time + Q_service.slide_window:
                        p_idx = e_idx
                if p_idx < 0:
                    Q_service.helper.logger.debug('Not enough data to dispatch')
                    return
                                    
                for a in A:
                    dispatch_data[d,s,a].append(total_data[d,s,a][0,e_idx])
                    # pop data
                    Q_service.med_data[med_id][d,s,a] = Q_service.med_data[med_id][d,s,a][p_idx:]
        
        # Call prediction service on dispatch data
        Q_service.pred_service.predict(med_id, u_id, dispatch_data)
        
             