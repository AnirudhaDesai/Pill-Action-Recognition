# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 18:45:20 2018

@author: amitrc
"""

import sys, os
sys.path.append(os.path.abspath('..'))
from FeatureExtraction import extract_features
import pickle
import numpy as np
from collections import defaultdict

TIMEOUT_WINDOW = 300 * 1000 # timeout for predict status in milliseconds

class PredictionService():
    m_twist, m_dispense, m_h2m, m_w2m = None, None, None, None
    db_session_factory = None
    helper = None
      
    user_predict_status = None
    
    def __init__(self):
        pass
    
    @staticmethod
    def start_service(sf, hlp, path):
        PredictionService.db_session_factory = sf
        PredictionService.helper = hlp
        PredictionService.m_twist = pickle.load(open(path + 'm_twist.pkl', 'rb'))
        PredictionService.m_dispense = pickle.load(open(path + 'm_dispense.pkl', 'rb'))
        PredictionService.m_h2m = pickle.load(open(path + 'm_h2m.pkl', 'rb'))
        PredictionService.m_w2m = pickle.load(open(path + 'm_w2m.pkl', 'rb'))
        PredictionService.user_predict_status = defaultdict(lambda : (hlp.STATUS_NO, -1))     # latest (status,time) of predicted "yes"
        
        
    @staticmethod
    def predict(medicine_id, user_id, data, cap_data, time):
        '''
        medicine_id : 
        user_id:
        data: nd array. data from accel,gyro.  
        cap_data = list of tuples [(state, timestamp)]
        time : start time of data window. To be stored in database if predicted
        '''        
        
        # check if prediction to be done based on status. 
        PredictionService.helper.logger.debug('Prediction initiated for medicine : %s', medicine_id)
        if not PredictionService.is_predicted(medicine_id, time):
            data = np.array([data])
            features = extract_features(data)
            
            p_twist = PredictionService.m_twist.predict(features)[0]
            p_dispense = PredictionService.m_dispense.predict(features)[0]
            p_h2m = PredictionService.m_h2m.predict(features)[0]
            p_w2m = PredictionService.m_w2m.predict(features)[0]
            
            net_pred = p_twist + p_dispense + p_h2m + p_w2m
            
            if net_pred >= 2:
                if p_twist == 1 or p_dispense == 1:
                    cur_session = PredictionService.db_session_factory()
                    installs = PredictionService.helper.get_all_installs(cur_session, 
                                                                         u_id=user_id)
                    meds = PredictionService.helper.get_all_medications(cur_session, 
                                                                        m_id=medicine_id)[0]
                    
                    push_ids = []
                    for install in installs:
                        push_ids.append(install.push_id)
                    
                    PredictionService.helper.send_push_notification(push_ids, 
                                                                    'Intake detected for - user: ' + user_id + ', medicine: ' + meds.m_name)
                    # update medicine prediction status
                    PredictionService.set_status(PredictionService.helper.STATUS_YES, medicine_id, time)
                    
    @staticmethod
    def is_predicted(med_id, time):
        #check if the prediction is already made for the user 
        # to be a 'Y' in the given window. If so, do not predict again.
        
        med_status = PredictionService.user_predict_status[med_id]
        
        if med_status[0] == PredictionService.helper.STATUS_NO:
            return False
        # latest prediction was true. check if within the window
        if time - med_status[1] > TIMEOUT_WINDOW:
            return False
        
        return True

    @staticmethod
    def set_status(status, med_id, time):
        # change status of the user. Can be called after prediction, after 
        # user replied to notification        
        PredictionService.user_predict_status[med_id] = (status, time)
    