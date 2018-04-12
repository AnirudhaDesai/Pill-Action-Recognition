#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 13:48:00 2018

@author: anirudha
"""

import os
from flask import Flask,jsonify, request
from flask import Response
import pandas as pd
import auth as au
from helpers import Helpers
import json
import sys
#import dill as pickle

app = Flask(__name__)
app.config.update(
JSONIFY_MIMETYPE = 'application/json'
)
global hp
hp = Helpers(app)      # all common methods/variables can go here
@app.route('/sign_in', methods = ['POST'])
def sign_in():
    response = '300'
#    app.logger.debug('mimetype : %s', str(app.config))
    
    try:

        values = request.form.to_dict()
        app.logger.info('json : %s', str(values))        
        id_token = values['idToken']
        client_id = values['id']
        response = au.verify_sign_in(id_token, client_id, hp)
        app.logger.info('Verifying sign in..')
        return (response)
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
        
    
    