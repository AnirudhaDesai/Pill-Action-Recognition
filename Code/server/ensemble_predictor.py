# -*- coding: utf-8 -*-
"""
Created on Fri May 25 09:49:58 2018

@author: amitrc
"""
import pickle, sys, os
sys.path.append(os.path.abspath('..'))
from FeatureExtraction import extract_features, FEATURE_ORDER
from predictor import Predictor
import numpy as np


class EnsemblePredictor(Predictor):
    
    def __init__(self, helper):
        super().__init__()
        models_path = helper.get_config('model', 'path')
        self.model_twist = pickle.load(open(models_path + 'm_twist.pkl', 'rb'))
        self.model_dispense = pickle.load(open(models_path + 'm_dispense.pkl', 'rb'))
        self.model_h2m = pickle.load(open(models_path + 'm_h2m.pkl', 'rb'))
        self.model_w2m = pickle.load(open(models_path + 'm_w2m.pkl', 'rb'))
        self.features_to_use = helper.get_config('model', 'features')
        self.logger = helper.logger
    
    
    def predict(self, data):
        sensor_data, _ = data
        sensor_data = np.array([sensor_data])
        all_features = extract_features(sensor_data)
        
        feature_to_use = '_'.join(self.features_to_use)
        feature_idx = FEATURE_ORDER.index(feature_to_use)
        
        p_twist = self.model_twist.predict(all_features[feature_idx])[0]
        p_dispense = self.model_dispense.predict(all_features[feature_idx])[0]
        p_h2m = self.model_h2m.predict(all_features[feature_idx])[0]
        p_w2m = self.model_w2m.predict(all_features[feature_idx])[0]
        
        net_pred = p_twist + p_dispense + p_h2m + p_w2m
        self.logger.debug('Prediction results (twist, dispense, h2m, w2m) : (%s,%s,%s,%s)', \
                    p_twist, p_dispense, p_h2m, p_w2m)
            
        if net_pred >= 2:
            if p_twist == 1 or p_dispense == 1:
                return True
        
        return False
        
        