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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import Install, User, Medication, Dosage, Intake, SensorReading, Base
from q_service import Q_service
from prediction_service import PredictionService
from concurrent.futures import ThreadPoolExecutor
import threading
import pprint
from flask_debugtoolbar import DebugToolbarExtension


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
sql_engine = create_engine('mysql+pymysql://amitrc:preparetest@localhost:3306/testing', 
                           pool_recycle=3600, 
                           echo=True)
Session = sessionmaker(bind=sql_engine)
Base.metadata.create_all(sql_engine)
PredictionService.start_service(Session, hp, '../../model/')
Q_service.start_service(hp)

# Standard responses
ENTRY_NOT_FOUND = ('', 204)
DEVICE_ALREADY_REGISTERED = ('Device already registered with same push_id', 500)
HOME_PAGE_SPLASH = ('<h2> Welcome to the DEV environment </h2>', 200)
DELETE_SUCCESS = ('Deletion complete', 200)
USER_ALREADY_EXISTS = ('Patient already exists with same patient Id', 500)
USER_ADD_SUCCESS = ('User Added Successfully', 201)
MEDICINE_ADD_SUCCESS = ('Medicines Added Successfully', 201)
INTAKE_ADD_SUCCESS = ('Intake info Added Successfully', 201)
DATA_ADD_REQUEST_COMPLETE = ('Successfully raised data add request', 201)


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
            ret_touch.append((float(fields[4]), int(fields[5])))
            continue
        
        m_id = int(fields[2])
        
        cur_readings = fields[4].split('~')
        ret[d_type, s_type, 0].append(float(cur_readings[0]))
        ret[d_type, s_type, 1].append(float(cur_readings[1]))
        ret[d_type, s_type, 2].append(float(cur_readings[2]))
        
        ret_tim[d_type, s_type].append(int(fields[5]))
        sensor_readings.append(SensorReading(user_id=u_id, 
                                             med_id=m_id,
                                             data=fields[0] + '`' + fields[1] + '`' + fields[4] + '`' + fields[5]))
    
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


@app.route('/create_user', methods=['POST'])
def create_user(make_new_user=True):
    req = request.get_json()
    
    u_id = req['u_id']
    p_id = req['p_id']
    meds = req['meds']
    dosages = req['dosages']
    
    cur_session = Session()
    m_ids = [hp.keygen(cur_session, Medication, Medication.med_id) for i in range(len(meds))]
    d_ids = [hp.keygen(cur_session, Dosage, Dosage.dosage_id) for i in range(len(dosages))]
        
    cur_meds = [Medication(user_id=u_id, med_id=m_ids[i], 
                           med_name=meds[i], 
                           dosage_id=d_ids[i]) for i in range(len(meds))]
    cur_dosages = [Dosage(dosage_id=d_ids[i], 
                          days=hp.stringify(dosages[i]['days']), 
                          times=hp.stringify(dosages[i]['times'])
                          ) for i in range(len(dosages))]
    
    if make_new_user == True:
        cur_user = User(user_id=u_id, patient_id=p_id)
        prev_user = cur_session.query(User).filter(
                    User.user_id == cur_user.user_id).first()
    
        if prev_user is not None:
            return USER_ALREADY_EXISTS
    
        cur_session.add(cur_user)
        
    cur_session.add_all(cur_meds)
    cur_session.add_all(cur_dosages)
    cur_session.commit()
    cur_session.close()
    if make_new_user == True:
        return USER_ADD_SUCCESS
    return MEDICINE_ADD_SUCCESS


@app.route('/add_medicine', methods=['POST'])
def add_medicine():
    create_user(make_new_user=False)
    

@app.route('/get_patient_list', methods=['GET'])
def get_patient_list():
    cur_session = Session()
    
    patient_list = cur_session.query(User).all()
    cur_session.commit()
    cur_session.close()
    
    ret = []
    for patient in patient_list:
        ret.append({'u_id': patient.user_id, 'p_id': patient.patient_id})
    
    return (jsonify(ret), 200)

@app.route('/get_medicine_data', methods=['GET'])
def get_medicine_data():
    u_id = request.headers['User-Id']
    st_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    
    if st_date is not None:
        st_date = dateparser.parse(st_date)
        end_date = dateparser.parse(end_date)
    
    cur_session = Session()
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
    
    cur_session.commit()
    cur_session.close()
    
    return (jsonify(ret), 200)
        

@app.route('/create_intake', methods=['POST'])
def create_intake():
    req = request.get_json()
    
    m_id = req['medicine_id']
    p_date = req['planned_date_time']
    a_date = req['actual_date_time']
    i_status = req['intake_status']
    
    cur_intake = Intake(med_id=m_id, 
                        actual_date=a_date, 
                        planned_date=p_date,
                        intake_status=i_status)
    
    cur_session = Session()
    cur_session.add(cur_intake)
    cur_session.commit()
    cur_session.close()
    
    return INTAKE_ADD_SUCCESS
    


    

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
    
    
