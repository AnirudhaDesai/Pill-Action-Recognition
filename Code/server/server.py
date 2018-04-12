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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import Install, Base



app = Flask(__name__)
app.config.update(
JSONIFY_MIMETYPE = 'application/json'
)
global hp

hp = Helpers(app)      # all common methods/variables can go here



#Create SQL engine, session-factory object and create all tables
sql_engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=sql_engine)
Base.metadata.create_all(sql_engine)


# Standard responses
ENTRY_NOT_FOUND = ('', 204)
DEVICE_ALREADY_REGISTERED = ('Device already registered with same push_id', 500)
HOME_PAGE_SPLASH = ('<h2> Welcome to the DEV environment </h2>', 200)
DELETE_SUCCESS = ('Deletion complete', 200)




@app.route('/sign_in', methods = ['POST'])
def sign_in():
    response = '300'
#    app.logger.debug('mimetype : %s', str(app.config))
    
    try:

        values = request.form.to_dict()
        app.logger.info('json : %s', str(values))        
        id_token = values['idToken']
        client_id = values['id']
        response = au.verify_sign_in_easy(id_token, client_id, hp)

        app.logger.info('Verifying sign in..')
        return (response)
    except Exception as e:
        raise e
        
@app.route('/register_device', methods = ['POST'])
def reg_device():
    p_id = request.form['push_id']
    i_id = request.headers['Install-Id']
    u_id = request.headers['User-Id']
    
    cur_install = Install(user_id=u_id, push_id=p_id, install_id=i_id)
    cur_session = Session()
    
    prev_install = cur_session.query(Install).filter(
                    Install.install_id == cur_install.install_id
                    ).first()
    
    if prev_install == None:
        cur_session.add(cur_install)
    elif prev_install.push_id == cur_install.push_id:
        return DEVICE_ALREADY_REGISTERED
    else:
        prev_install.push_id = cur_install.push_id
    
    cur_session.commit()
    cur_session.close()
    return ('Device succesfully added - ' + 'push_id = ' + p_id + 
            ' install_id = ' + i_id + '  user_id = ' + u_id,
            201)


@app.route('/upload_sensor_readings', methods = ['POST'])
def upload_sensor_readings():
    pass

@app.route('/', methods=['GET'])
def index():
    return HOME_PAGE_SPLASH

@app.route('/get_install/', methods=['GET'])
def get_install():
    cur_session = Session()
    cur_installs = hp.query_installs(request, cur_session)
    cur_session.close()
    
    if cur_installs == None:
        return ENTRY_NOT_FOUND
    
    ret = ''
    for cur_install in cur_installs:
        ret = ret + cur_install.__repr__()
        
    return (ret, 200)

@app.route('/remove_install/', methods=['DELETE'])
def remove_install():
    cur_session = Session()
    cur_installs = hp.query_installs(request, cur_session)
    
    if cur_installs == None:
        cur_session.close()
        return ENTRY_NOT_FOUND
    
    for cur_install in cur_installs:
        cur_session.delete(cur_install)
    cur_session.commit()
    cur_session.close()
    
    return DELETE_SUCCESS
    
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
        
    
    
