#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 13:48:00 2018

@author: anirudha
"""

import os
from flask import Flask,jsonify, request
import pandas as pd
import dill as pickle

app = Flask(__name__)
@app.route('/predict', methods = ['POST'])
def apicall():
    try:
        data_json = request.get_json()
        data = pd.read_json(data_json, orient='records')
    except Exception as e:
        raise e
    
    print data
    
    responses = jsonify(predictions = 'Predictions will be here')
    responses.status_code = 200
    return (responses)
#    clf = 'ML_model_v1.pk'
#    
#    print ('Loading the model .. ')
#    model = None
#    with open('./models/'+clf, 'rb') as f:
#        model = pickle.load(f)
#        
        
    
    