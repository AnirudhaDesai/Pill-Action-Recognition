#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 13:48:00 2018

@author: anirudha
"""

from flask import Flask,jsonify, request, render_template
from flask import make_response
import auth as au
from helpers import Helpers
from dateutil import parser as dateparser
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import Install, User, Medication, Dosage, Intake, SensorReading, PredictionTime, Base
from q_service import Q_service
from prediction_service import PredictionService
from concurrent.futures import ThreadPoolExecutor
import threading
from flask_debugtoolbar import DebugToolbarExtension
from collections import defaultdict
import numpy as np


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = '0799'
toolbar = DebugToolbarExtension(app)

app.config.update(
JSONIFY_MIMETYPE = 'application/json'
)

global hp
async_executor = ThreadPoolExecutor(max_workers = 50)

hp = Helpers(app)      # all common methods/variables can go here



# Create SQL engine, session-factory object and create all tables
# These are my own credentials for my local MySql Server, you need
# to use your own server credentials when running locally or use
# in memory sqlite - create_engine('sqlite:///:memory:', echo = True)
db_user = hp.get_config('db', 'user')
db_pass = hp.get_config('db', 'password')
db_name = hp.get_config('db', 'name')
db_port = str(hp.get_config('db', 'port'))
sql_engine = create_engine('mysql+pymysql://'+db_user+':'+db_pass+'@localhost:'+db_port+'/'+db_name, 
                           pool_recycle=3600, 
                           echo=True)
Session = sessionmaker(bind=sql_engine)
Base.metadata.create_all(sql_engine)
PredictionService.start_service(Session, hp)
Q_service.start_service(hp)

ACTION_WINDOW = hp.get_config('model', 'action_window')
API_KEY = hp.get_config('basic', 'api_key')
AUTHORIZED_USER = hp.get_config('basic', 'authorized_user')
SECURE_SERVER = hp.get_config('basic', 'security')

# Standard responses
ENTRY_NOT_FOUND = ('', 204)
DEVICE_ALREADY_REGISTERED = ('Device already registered with same push_id', 200)
DELETE_SUCCESS = ('Deletion complete', 200)
USER_ALREADY_EXISTS = ('Patient already exists with same patient Id', 500)
USER_ADD_SUCCESS = ('Patient Added Successfully', 201)
USER_ADD_FAILED = ('Failed to add patient', 400)
USER_DOES_NOT_EXIST = ('The specified patient does not exist', 400)
MEDICINE_ADD_SUCCESS = ('Medicines Added Successfully', 201)
MEDICINE_ADD_FAILED = ('Medicine add failed', 400)
MEDICINE_NOT_FOUND = ('Medicine does not exist', 400)
MEDICINE_REMOVE_SUCCESS = ('Medicine removed successfully', 200)
INTAKE_ADD_SUCCESS = ('Intake info Added Successfully', 201)
DATA_ADD_REQUEST_COMPLETE = ('Successfully raised data add request', 201)
CONFIG_RESET_SUCCESS = ('Successfully reset config file', 200)
DOSAGE_ADD_FAILED = ('Failed to add/update dosage info', 400)
DOSAGE_ADD_SUCCESS = ('Successfully added/updated dosage info', 201)
DATA_EXTRACTION_COMPLETE = ('data extraction complete', 200)
ACCESS_DENIED = ('ACCESS DENIED', 401)

@app.before_request
def verify_token():
    if SECURE_SERVER == 'ON':
        api_key = request.headers.get('X-Api-Key', None)
        if api_key is not None:
            if api_key != API_KEY:
                print('Unauthorized access request', api_key)
                return ACCESS_DENIED
        elif request.args.get('user', None) != AUTHORIZED_USER:
            print('Unauthorized access request')
            return ACCESS_DENIED
    
    return None
    

@app.route('/sign_in', methods = ['POST'])
def sign_in():

    try:
        app.logger.info('Verifying sign in...')
        values = request.get_json()
        app.logger.debug('json : %s', str(values))        
        id_token = values['id_token']
        access_token = au.verify_sign_in(id_token, hp)
    except Exception as e:
        print ("Exception in sign in : " , e)
        return make_response('',400)
    if access_token == None:
        app.logger.info('Problem encountered in sign in')
        return make_response('',400)
    resp = {"access_token" : access_token}
    response = make_response(jsonify(resp), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
        
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
    
    if prev_install is None:
        cur_session.add(cur_install)
    elif prev_install.user_id != cur_install.user_id:
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
    u_id = request.headers['User-Id']
    
    data = request.get_json()
    ret = hp.get_clean_data_array((2,2,3))
    ret_tim = hp.get_clean_data_array((2,2))
    ret_touch = []
    sensor_readings = []
    
    for entry in data:
        fields = entry.split('`')
        d_type = int(fields[0])
        s_type = int(fields[1])
        
        if s_type == 2:
            ret_touch.append((int(fields[4]), int(fields[5])))
            continue
        
        m_id = int(fields[2])
        
        cur_readings = fields[4].split('~')
        ret[d_type, s_type, 0].append(float(cur_readings[0]))
        ret[d_type, s_type, 1].append(float(cur_readings[1]))
        ret[d_type, s_type, 2].append(float(cur_readings[2]))
        
        ret_tim[d_type, s_type].append(float(fields[5]))
        sensor_readings.append(SensorReading(user_id=u_id, 
                                             med_id=m_id,
                                             sensor_location=str(d_type),
                                             sensor_type=str(s_type),
                                             data=fields[4],
                                             time=fields[5]))
    
    print('Moving on to different thread for async call, current thread -', threading.current_thread())
    async_executor.submit(Q_service.enqueue, ret, ret_tim, ret_touch, m_id, u_id)
    print('Spawned new thread for async call, now back to original thread', threading.current_thread())
    
    cur_session = Session()
    cur_session.add_all(sensor_readings)
    cur_session.commit()
    cur_session.close()
    
    return DATA_ADD_REQUEST_COMPLETE
    
@app.route('/', methods=['GET'])
def index():
    return render_template('homepage.html')


@app.route('/create_user', methods=['POST', 'OPTIONS'])
def create_user(make_new_user=True):
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    req = request.get_json()
    
    u_id = None
    if make_new_user == True:
        u_id = hp.read_user_id(req['u_id'])
        if len(u_id) == 0:
            return USER_ADD_FAILED
        
    p_id = req['p_id']
    
    if len(p_id) == 0:
        if make_new_user == True:
            return USER_ADD_FAILED
        return MEDICINE_ADD_FAILED
    
    meds = req['med_names']
    dosages = req['dosages']
    
    if len(meds) == 0 or len(dosages) == 0:
        if make_new_user == True:
            return USER_ADD_FAILED
        return MEDICINE_ADD_FAILED
    
    cur_session = Session()
    m_ids = [hp.keygen(cur_session, Medication, Medication.med_id) for i in range(len(meds))]
    d_ids = [hp.keygen(cur_session, Dosage, Dosage.dosage_id) for i in range(len(dosages))]
    
    if u_id is None:
        cur_user = cur_session.query(User).filter(User.patient_id == p_id).first()
        if cur_user is None:
            cur_session.close()
            return MEDICINE_ADD_FAILED
        u_id = cur_user.user_id
    cur_meds = [Medication(user_id=u_id, med_id=m_ids[i], 
                           med_name=meds[i], 
                           dosage_id=d_ids[i],
                           validation_date=(datetime.now()-timedelta(days=1)).isoformat()) for i in range(len(meds))]
    cur_dosages = [Dosage(dosage_id=d_ids[i], 
                          days=hp.stringify(dosages[i]['days']), 
                          times=hp.stringify(dosages[i]['times'])
                          ) for i in range(len(dosages))]
    
    if make_new_user == True:
        cur_user = User(user_id=u_id, patient_id=p_id)
        prev_user = cur_session.query(User).filter(
                    User.user_id == cur_user.user_id).first()
    
        if prev_user is not None:
            cur_session.close()
            return USER_ALREADY_EXISTS
    
        cur_session.add(cur_user)
        
    cur_session.add_all(cur_meds)
    cur_session.add_all(cur_dosages)
    cur_session.commit()
    cur_session.close()
    if make_new_user == True:
        return USER_ADD_SUCCESS
    return MEDICINE_ADD_SUCCESS

@app.route('/remove_user', methods=['POST', 'OPTIONS'])
def remove_user():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    req = request.get_json()
    
    p_id = req['p_id']
    
    cur_session = Session()
    cur_user = cur_session.query(User).filter(User.patient_id == p_id).first()
    
    if len(p_id) == 0 or cur_user is None:
        cur_session.close()
        return USER_DOES_NOT_EXIST
    
    u_id = cur_user.user_id
    
    cur_session.query(Install).filter(Install.user_id == u_id).delete()
    cur_session.query(User).filter(User.user_id == u_id).delete()
    meds = cur_session.query(Medication).filter(Medication.user_id == u_id).all()
    
    for med in meds:
        #TODO : Might not want to remove all intake info
        cur_session.query(Intake).filter(Intake.med_id == med.med_id).delete()
        cur_session.query(Dosage).filter(Dosage.dosage_id == med.dosage_id).delete()
        # Need to keep data in Medication table to make training data
        # cur_session.delete(med)
    
    
    cur_session.commit()
    cur_session.close()
    
    return DELETE_SUCCESS

@app.route('/add_medicine', methods=['POST'])
def add_medicine():
    return create_user(make_new_user=False)
    
@app.route('/remove_medicine', methods=['POST', 'OPTIONS'])
def remove_medicine():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    req = request.get_json()
    m_id = req['med_id']
    
    cur_session = Session()
    cur_med = cur_session.query(Medication).filter(Medication.med_id == m_id).first()
    
    if cur_med is None:
        return MEDICINE_NOT_FOUND
    
    cur_session.query(Dosage).filter(Dosage.dosage_id == cur_med.dosage_id).delete()
    cur_session.query(Intake).filter(Intake.med_id == cur_med.med_id).delete()
    
    # Need to keep data in Medication table, gets used to create training data
    # cur_session.delete(cur_med)
    cur_session.commit()
    cur_session.close()
    
    return MEDICINE_REMOVE_SUCCESS
    

@app.route('/get_patient_list', methods=['GET'])
def get_patient_list():
    cur_session = Session()
    
    patient_list = cur_session.query(User).all()
    cur_session.close()
    
    ret = []
    for patient in patient_list:
        ret.append({'u_id': patient.user_id, 'p_id': patient.patient_id})
    
    return (jsonify(ret), 200)

@app.route('/get_medicine_data', methods=['GET', 'OPTIONS'])
def get_medicine_data():
    if request.method == 'OPTIONS':
        return handle_preflight()
    
    cur_session = Session()
    if 'User-Id' in request.headers:
        u_id = request.headers['User-Id']
    else:
        p_id = request.headers['Patient-Id']
        u_id = cur_session.query(User).filter(
                User.patient_id == p_id
                ).first().user_id
    st_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    
    if st_date is not None:
        st_date = dateparser.parse(st_date)
        end_date = dateparser.parse(end_date)
    
    meds = cur_session.query(Medication).filter(Medication.user_id == u_id).all()
    
    ret = {'medicines': [], 'dosages': [], 'intakes': []}
    
    for med in meds:
        cur_med = {'id': med.med_id, 
               'name': med.med_name, 
               'image_url': 'https://aidsinfo.nih.gov/images/drugimages/full/truvada.jpg'}
        ret['medicines'].append(cur_med)
        
        dose = cur_session.query(Dosage).filter(Dosage.dosage_id == med.dosage_id).first()
        cur_dose = {'medicine_id': med.med_id,
                    'days': dose.get_days(),
                    'times': dose.get_times()}
        ret['dosages'].append(cur_dose)
        
        hp.validate_intakes(med, dose, cur_session)
        intakes = cur_session.query(Intake).filter(Intake.med_id == med.med_id).all()
        for intake in intakes:
            if st_date is not None:
                cur_date = dateparser.parse(intake.planned_date)
                if cur_date > end_date or cur_date < st_date:
                    continue
                
            cur_intake = {'medicine_id': med.med_id,
                          'planned_date_time': intake.planned_date,
                          'actual_date_time': intake.actual_date,
                          'intake_status': intake.intake_status}
            ret['intakes'].append(cur_intake)
    
    cur_session.close()
    
    return (jsonify(ret), 200)
        

@app.route('/create_intake', methods=['POST'])
def create_intake():
    req = request.get_json()
    
    m_id = req['medicine_id']
    p_date = req['planned_date_time']
    a_date = req['actual_date_time']
    
    i_status = 3
    if a_date is not None and len(a_date)>0:
        i_status = hp.get_intake_status(p_date, a_date)
    
    if i_status != 3:
        PredictionService.confirm_intake(m_id, dateparser.parse(a_date))
    
    cur_intake = Intake(med_id=m_id, 
                        actual_date=a_date, 
                        planned_date=p_date,
                        intake_status=i_status)
    
    cur_session = Session()
    prev_intake = cur_session.query(Intake).filter(Intake.med_id == m_id).filter(Intake.planned_date == p_date).first()
    
    if prev_intake is not None:
        prev_intake.actual_date = cur_intake.actual_date
        prev_intake.intake_status = cur_intake.intake_status
    else:
        cur_session.add(cur_intake)
    cur_session.commit()
    cur_session.close()
    
    return INTAKE_ADD_SUCCESS

@app.route('/update_dosage', methods = ['POST'])
def update_dosage():
    req = request.get_json()
    
    m_id = req['med_id']
    dosage = req['dosages'][0]
    
    cur_session = Session()
    prev_med = cur_session.query(Medication).filter(Medication.med_id == m_id).first()
    if prev_med is None:
        cur_session.close()
        return DOSAGE_ADD_FAILED
    
    prev_dosage = cur_session.query(Dosage).filter(Dosage.dosage_id == prev_med.dosage_id).first()
    
    if prev_dosage is None:
        cur_session.close()
        return DOSAGE_ADD_FAILED
    
    prev_dosage.days = hp.stringify(dosage['days'])
    prev_dosage.times = hp.stringify(dosage['times'])
    
    cur_session.commit()
    cur_session.close()
    return DOSAGE_ADD_SUCCESS
        
    
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

@app.route('/remove_install', methods=['DELETE'])
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

@app.route('/reset_config', methods=['POST'])
def reset_config():
    global hp
    hp = Helpers(app)
    Q_service.start_service(hp)
    PredictionService.start_service(Session, hp)
    return CONFIG_RESET_SUCCESS


@app.route('/extract_training_data', methods=['GET'])
def extract_training_data():
    '''
    This code probably has lots of bugs!!
    Going in untested.
    '''
    global hp
    cur_session = Session()
    
    sensor_data_list = cur_session.query(SensorReading).all()
    predictions_list = cur_session.query(PredictionTime).all()
    medications_list = cur_session.query(Medication).all()
    
    cur_session.close()
    
    predictions = defaultdict(list)
    sensor_data = defaultdict(list)
    
    for pred in predictions_list:
        predictions[pred.med_id].append(pred)
    for s_data in sensor_data_list:
        sensor_data[s_data.med_id].append(s_data)
    
    read_time = lambda x: float(x.time)
    all_data = []
    all_labels = []
    
    for med in medications_list:
        cur_preds = predictions[med.med_id]
        cur_data = sensor_data[med.med_id]
        
        cur_preds.sort(key=read_time)
        cur_data.sort(key=read_time)
        
        negative_pile = []
        positive_samples = []
        end_idx = 0
        for pred in cur_preds:
            start_idx = lower_bound(cur_data, float(pred.time), read_time, first_idx=end_idx)
            negative_pile.extend(cur_data[end_idx:start_idx])
            end_idx = lower_bound(cur_data, float(pred.time) + ACTION_WINDOW, read_time, first_idx=start_idx)
            positive_samples.append(cur_data[start_idx:end_idx])
        
        pos_data = get_data(positive_samples)
        
        negative_samples = []
        start_idx = 0
        cur_sample = []
        for item in negative_pile:
            if read_time(item) - read_time(negative_pile[start_idx]) >= ACTION_WINDOW:
                negative_samples.append(cur_sample)
                cur_sample = []
            cur_sample.append(item)
        if len(cur_sample) > 0:
            negative_samples.append(cur_sample)
        
        neg_data = get_data(negative_samples)
        data = pos_data + neg_data
        all_data.extend(data)
        labels = [0]*len(data)
        for i in range(len(pos_data)):
            labels[i] = 1
        all_labels.extend(labels)
    
    all_data = np.array(all_data)
    all_labels = np.array(all_labels)
    
    path = hp.get_config('model', 'path_to_data')
    np.savez(path + 'combined_data.npz', all_data, all_labels)
    
    return DATA_EXTRACTION_COMPLETE
        

@app.after_request
def decorate_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

def handle_preflight():
    resp = Flask.response_class('')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'User-Id, Patient-Id'
    resp.headers['Content-Type'] = 'text/html'
    return resp

def lower_bound(lst, bound, key, first_idx=0):
    for idx in range(first_idx, len(lst)):
        if key(lst[idx]) >= bound:
            return idx
    return len(lst)

def get_data(samples):
    data = []
    for sample in samples:
        data_item = hp.get_clean_data_array((2,2,3))
        for reading in sample:
            d_type = int(reading.sensor_location)
            s_type = int(reading.sensor_type)
            
            x_d, y_d, z_d = reading.data.split('~')
            data_item[d_type, s_type, 0].append(x_d)
            data_item[d_type, s_type, 1].append(y_d)
            data_item[d_type, s_type, 2].append(z_d)
        data.append(data_item)
    return data