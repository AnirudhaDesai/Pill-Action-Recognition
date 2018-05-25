# -*- coding: utf-8 -*-
"""
Created on Fri May 25 09:30:23 2018

@author: amitrc
"""

from predictor import Predictor

class TouchPredictor(Predictor):
    
    def __init__(self, helper):
        super().__init__()
        self.touch_threshold = helper.get_config('model', 'touch_threshold')
        self.logger = helper.logger
    
    def predict(self, data):
        _, touch_data = data
        self.logger.debug('Making prediction using touch-based model...')
        max_interaction_duration = 0
        cur_touch = touch_data[0]
        for i in range(len(touch_data)):
            if cur_touch[0] == touch_data[i][0]:
                continue
            
            if cur_touch[0] == 1:
                max_interaction_duration = max(max_interaction_duration, 
                                               touch_data[i][1] - cur_touch[1])
            cur_touch = touch_data[i]
        
        pred = False
        if max_interaction_duration > self.touch_threshold:
            pred = True
        
        self.logger.debug('Prediction using touch model - ' + str(pred))
        return pred