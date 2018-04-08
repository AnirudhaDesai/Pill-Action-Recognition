#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 13:48:00 2018

@author: anirudha
"""

import os
from flask import Flask,jsonify, request
import pandas as pd
import auth as au
from helpers import Helpers
import json
#import dill as pickle

app = Flask(__name__)
global hp
hp = Helpers()      # all common methods/variables can go here
@app.route('/sign_in', methods = ['POST'])
def sign_in():
    try:
        values = json.loads(request.get_json())
        id_token = values['id_token']
        responses = au.verify_sign_in(id_token, hp)
        app.logger.info('Verifying sign in..')
        return (responses)
    except Exception as e:
        raise e
        
@app.route('/register_device', methods = ['POST'])
def reg_device():
    
    pass
@app.route('/upload_sensor_readings', methods = ['POST'])
def upload_sensor_readings():
    pass
        
#        
#@app.route('/predict', methods = ['POST'])
#def apicall():
#    try:
#        data_json = request.get_json()
#        data = pd.read_json(data_json, orient='records')
#    except Exception as e:
#        raise e
#    
##    print (data)
#    
#    responses = jsonify(predictions = 'Predictions will be here')
#    responses.status_code = 200
#    return (responses)
#    clf = 'ML_model_v1.pk'
#    
#    print ('Loading the model .. ')
#    model = None
#    with open('./models/'+clf, 'rb') as f:
#        model = pickle.load(f)
#        
        
    
    