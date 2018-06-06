# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 09:03:30 2018

@author: amitrc
"""

import pickle, sys, os
sys.path.append(os.path.abspath('..'))
from FeatureExtraction import extract_features, FEATURE_ORDER
from predictor import Predictor
import numpy as np

class BinaryPredictor(Predictor):
    
    def __init__(self, helper):
        super().__init__()
        model_path = helper.get_config('model', 'path')
        self.model = pickle.load(open(model_path + 'binary_classifier.pkl', 'rb'))
        self.features_to_use = helper.get_config('model', 'features')
        self.logger = helper.logger
    
    def predict(self, data):
        sensor_data, _ = data
        sensor_data = np.array([sensor_data])
        
        all_features = extract_features(sensor_data)
        
        feature_to_use = '_'.join(self.features_to_use)
        feature_idx = FEATURE_ORDER.index(feature_to_use)
        
        pred = self.model.predict(all_features[feature_idx])[0]
        self.logger.debug('Prediciton made by binary classifier - ' + str(pred))
        
        return pred