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

class PredictionService():
    m_twist, m_dispense, m_h2m, m_w2m = None, None, None, None
    db_session_factory = None
    helper = None
    
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
    
    @staticmethod
    def predict(medicine_id, user_id, data):
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
        