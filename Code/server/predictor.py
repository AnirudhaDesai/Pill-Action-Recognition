# -*- coding: utf-8 -*-
"""
Created on Fri May 25 09:22:05 2018

@author: amitrc
"""

from abc import ABC as AbstractClass, abstractmethod

class Predictor(AbstractClass):
    
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def predict(self, data):
        pass
    