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
import copy


SLIDE_WINDOW = 1 * 1000   # number of milliseconds to slide 
T_WINDOW = 4 * 1000      # Time window for dispatch (in milliseconds)


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
        Q_service.helper.logger.debug('Executing Q_service on thread : %s', str(threading.current_thread()))
        D,S,A = Q_service.med_data[medicine_id].shape
        Q_service.med_touches[medicine_id].extend(touches)
        print("input data : ", data)
        cur_data = Q_service.med_data[medicine_id]
        cur_tims = Q_service.med_timestamps[medicine_id]
        for d in range(D):
            for s in range(S):
                Q_service.helper.logger.debug('d,s, cur_tims[d,s], tims[d,s] :%s,%s   %s --- %s', d,s,str(cur_tims[d,s]), str(tims[d,s]))
                
#                ts_list = copy.deepcopy(cur_tims[d,s])
#                print(ts_list)
#                ts_list.extend(tims[d,s])
                cur_tims[d,s].extend(copy.deepcopy(tims[d,s]))
#                print(ts_list)
#                cur_tims[d,s] = copy.deepcopy(ts_list)
                for a in range(A):
                    
#                    ts_list = copy.deepcopy(cur_data[d,s,a])
#                    ts_list.extend(data[d,s,a])
#                    cur_data[d,s,a] = copy.deepcopy(ts_list)
                    cur_data[d,s,a].extend(copy.deepcopy(data[d,s,a]))
                    print('cur data : ', cur_data )
        
        print(Q_service.med_data[medicine_id])
                    
                    
        # check if timestamp duration is sufficient for prediction. 
        # Using 0,0 for reference
        
        start = cur_tims[0,0][0]
        
        if Q_service.check_data_for_dispatch(medicine_id):
                
            Q_service.dispatch(medicine_id,user_id, start)
        

    def check_data_for_dispatch(medicine_id):
        # Make this function more robust by considering more timestamps if needed
        cur_tims = Q_service.med_timestamps[medicine_id]
        start = cur_tims[0,0][0]
        end = cur_tims[0,0][-1]
        Q_service.helper.logger.debug('start, end (medicine_id, delta_T) :%s, %s (%s, %s)',\
                        start, end, str(medicine_id),str(end - start))
        if end-start > T_WINDOW:
            return True
        else:
            return False
    
    def dispatch(med_id, u_id, start):
        
        Q_service.helper.logger.debug('Dispatch initiated for medicine id: %s', str(med_id))
        total_data = Q_service.med_data[med_id]
        print("total_data : ",total_data)
        times = Q_service.med_timestamps[med_id]
        touches = Q_service.med_touches[med_id]
        
        
        D,S,A = Q_service.med_data[med_id].shape
        
        dispatch_data = Q_service.helper.get_clean_data_array((D,S,A))
        disp_cap_data = []
        
        for d in range(D):
            for s in range(S):
                s_time = times[d,s][0]
                Q_service.helper.logger.debug("s_time, d,s,times[d,s] :%s,%s, %s, %s", s_time, d, s, times[d,s])
                del_idx, send_idx = get_index(times[d,s], s_time + SLIDE_WINDOW, s_time + T_WINDOW)
                
                if send_idx == 0:
                    Q_service.helper.logger.debug('Not enough data to dispatch!')
                    return
                                    
                for a in range(A):
#                    Q_service.helper.logger.debug("sensor data del_idx, send_idx : %s, %s", del_idx, send_idx)
                    
                    dispatch_data[d,s,a] = copy.deepcopy(total_data[d,s,a][:send_idx-1])
                    Q_service.med_data[med_id][d,s,a] = Q_service.med_data[med_id][d,s,a][del_idx:]
                    
                Q_service.med_timestamps[med_id][d,s] = Q_service.med_timestamps[med_id][d,s][del_idx:]
        
        # Optimize this later
        touch_ts = [k[1] for k in touches]      # timestamps extracted from list of tuples
        Q_service.helper.logger.debug('Calling predict for medicine id : %s ', str(dispatch_data))
        del_idx, send_idx = get_index(touch_ts, touches[0][1] + SLIDE_WINDOW, touches[0][1] + T_WINDOW)
        if send_idx == 0:
            Q_service.helper.logger.debug('Not enough capacitive data to dispatch!')
            return
        Q_service.helper.logger.debug("Cap data del_idx, send_idx : %s, %s", del_idx, send_idx)
        Q_service.med_touches[med_id] = Q_service.med_touches[med_id][del_idx:]
        disp_cap_data = Q_service.med_touches[med_id][:send_idx-1]
        
        PredictionService.predict(med_id, u_id, dispatch_data, disp_cap_data, start)
        
             
