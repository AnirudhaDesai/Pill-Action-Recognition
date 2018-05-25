# -*- coding: utf-8 -*-
"""
Created on Fri May 25 10:03:18 2018

@author: amitrc
"""

from touch_predictor import TouchPredictor
from ensemble_predictor import EnsemblePredictor


class PredictorFactory:
    
    def __init__(self):
        pass
    
    @staticmethod
    def create_predictor(helper):
        pred_type = helper.get_config('model', 'type')
        helper.logger.debug('Using model type - ' + str(pred_type))
        if pred_type == 'Ensemble':
            return EnsemblePredictor(helper)
        elif pred_type == 'Touch':
            return TouchPredictor(helper)
    