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
from prediction_service import PredictionService


SLIDE_WINDOW = 1 * 1000   # number of milliseconds to slide 
T_WINDOW = 10 * 1000      # Time window for dispatch (in milliseconds)


# Get the indices for first number greater than val1 
# and val2 in sorted array ar.
# val2 is optional.
# TODO: switch to binary search
def get_index(ar, val1, val2=1e50):
    idx1, idx2 = len(ar), len(ar)
    for i in range(len(ar)):
        if ar[i] > val1:
            idx1 = min(idx1, i)
            if (ar[i] > val2):
                idx2 = i
                break
    
    return idx1, idx2

def default_fill(tupl):
    return Q_service.helper.get_clean_data_array(tupl)

class Q_service:
    helper = None
    med_data = defaultdict(lambda : default_fill((2, 2, 3)))
    med_timestamps = defaultdict(lambda : default_fill((2, 2)))
    med_touches = defaultdict(list)    
    
    # This method is here but do not use.
    def __init__(self, hp):
        pass
    @staticmethod 
    def start_service(hp):
        Q_service.helper = hp
        
    @staticmethod
    def enqueue(data, 
                tims,
                touches,
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
        D,S,A = Q_service.med_data[medicine_id].shape
        Q_service.med_touches[medicine_id].extend(touches)
        
        cur_data = Q_service.med_data[medicine_id]
        cur_tims = Q_service.med_timestamps[medicine_id]
        for d in range(D):
            for s in range(S):
                for a in range(A):
                    cur_data[d,s,a].extend(data[d,s,a])
                    cur_tims[d,s].extend(tims[d,s])
            
        # check if timestamp duration is sufficient for prediction. 
        # Using 0,0 for reference
        start = cur_tims[0,0][0]
        end = cur_tims[0,0][-1]
        if end-start > T_WINDOW:
            Q_service.dispatch(medicine_id,user_id, start)

        print('Executing Q_service on thread', threading.current_thread())
    
    def dispatch(med_id, u_id, start):
        total_data = Q_service.med_data[med_id]
        times = Q_service.med_timestamps[med_id]
        touches = Q_service.med_touches[med_id]
        
        D,S,A = Q_service.med_data[med_id].shape
        dispatch_data = Q_service.hp.get_clean_data_array((D,S,A))
        
        for d in range(D):
            for s in range(S):
                s_time = times[d,s][0]
                
                del_idx, send_idx = get_index(times[d,s], s_time + SLIDE_WINDOW, s_time + T_WINDOW)
                if send_idx == 0:
                    Q_service.helper.logger.debug('Not enough data to dispatch')
                    return
                                    
                for a in A:
                    dispatch_data[d,s,a].extend(total_data[d,s,a][:send_idx-1])
                    Q_service.med_data[med_id][d,s,a] = Q_service.med_data[med_id][d,s,a][del_idx:]
                    
                Q_service.med_timestamps[med_id][d,s] = Q_service.med_timestamps[med_id][d,s][del_idx:]
        
        del_idx, send_idx = get_index(touches, touches[0][1] + SLIDE_WINDOW, touches[0][1] + T_WINDOW)
        Q_service.med_touches[med_id] = Q_service.med_touches[med_id][del_idx:]
        
        PredictionService.predict(med_id, u_id, dispatch_data, start)
        
             