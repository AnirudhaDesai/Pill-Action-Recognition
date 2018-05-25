# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 16:24:08 2018

@author: anirudha
"""
import requests

import json
import numpy as np
from tables import Install, Medication, Intake
from pyfcm import FCMNotification
from hashlib import sha256 as sha2
from dateutil import parser
from datetime import datetime, timedelta


CONFIG_PATH = '../config.json'

class Helpers:
    def __init__(self,flask_app):
        self.logger = flask_app.logger
        apikey = "AAAAgOfyS6s:APA91bH0GGnd4Xvw_pWMDpGmsQrR79CU8_bOmDj2QsHyrpua89dwV_UUAcJNRELByd_uikq4Hd5oI-ik6uWoW9i4w3qgtdqqg8TYKwwhAg-HllaBKoIdAy9yF1tvIGaAUvXGLtdIzTqF"                 # api key from FCM for the app
        self.push_service = FCMNotification(api_key = apikey)
        self.STATUS_YES = 'Y'
        self.STATUS_NO = 'N'
        self.all_days = ['Monday', 'Tuesday', 
                         'Wednesday', 'Thursday', 
                         'Friday', 'Saturday', 'Sunday']
        self.config = json.load(open(CONFIG_PATH))
        self.client_id = self.get_config('basic', 'client_id')        
        
    def get_config(self, *args):
        ret = self.config
        for i in range(len(args)):
            ret = ret[args[i]]
        return ret

    def build_url(self,addr,*args):
        '''
    
        :param addr: Address
        :param args: list of components in the url. Will be appended with '/'
        :return:   returns the formatted url
        '''
        comp=''
    
        for i in range(len(args)-1):
            comp += args[i]+'/'
        comp += args[len(args)-1]
        
        url = urllib.parse.urljoin("http://"+addr,comp)
        logger.debug('Built url : ', url)
        return url
    
    def get_request(self,url,data=None):
        '''
    
        :param url: url to send the get request
        :param params: params to append to the query
        :return: response from the server
        '''
        response = None
    
        try:
            self.logger.debug('GET request : %s', url)
            params = json.dumps(data)
            self.logger.debug(str(params))
            response = requests.get(url,params=params)
    
        except Exception as e:
            print(e)
    
        return response
    
    def query_installs(self, request, cur_session):
        '''
        
        queries Install table according to all ids supplied
        in request object
        :param request: current request context
        :param cur_session: current database session object
        :returns: List of matching entries if present, None otherwise
        '''
        u_id = self.read_user_id(request.args.get('u_id', None))
        i_id = request.args.get('i_id', None)
        p_id = request.args.get('p_id', None)
        
        return self.get_all_installs(cur_session, u_id, i_id, p_id)
    
    def get_all_installs(self, cur_session, u_id=None, i_id=None, p_id=None):
        if i_id is None and p_id is None and u_id is None:
            return None
        
        if i_id is not None:
            cur_installs = cur_session.query(Install).filter(Install.install_id == i_id).all()
        elif u_id is not None:
            cur_installs = cur_session.query(Install).filter(Install.user_id == u_id).all()
        else:
            cur_installs = cur_session.query(Install).filter(Install.push_id == p_id).all()
        
        if len(cur_installs) == 0:
            return None
        return cur_installs
    
    def get_all_medications(self, cur_session, 
                       m_id=None, m_name=None, u_id=None, d_id=None):
        if m_id is None and u_id is None and d_id is None and m_name is None:
            return None
        
        if m_id is not None:
            cur_meds = cur_session.query(Medication).filter(
                        Medication.med_id == m_id).all()
        elif u_id is not None:
            cur_meds = cur_session.query(Medication).filter(
                        Medication.user_id == u_id).all()
        elif m_name is not None:
            cur_meds = cur_session.query(Medication).filter(
                        Medication.med_name == m_name).all()
        else:
            cur_meds = cur_session.query(Medication).filter(
                        Medication.dosage_id == d_id).all()
        
        if len(cur_meds) == 0:
            return None
        return cur_meds
    
    def keygen(self, cur_session, cur_table, table_attr):
        key = np.random.randint(0, 2**31)
        prev_entry = cur_session.query(cur_table).filter(table_attr == key).first()
        if prev_entry is not None:
            return self.keygen(cur_session, cur_table, table_attr)
        return key
    
    def stringify(self, lst):
        ret = ''
        for s in lst:
            ret += ',' + s
        return ret[1:]
    
    def send_push_notification(self, reg_id_list, data_message=None):
        '''
        : param reg_id_list: list of registration ids
        : param data_message: optional payload with custom key-value pairs
        : returns: Sends out push notification to multiple devices.response data from pyFCM 
        '''
        if len(reg_id_list) == 0:
            self.logger.debug('No registration ids to send push notification to')
            return
        if len(reg_id_list) == 1:
            self.logger.debug('Making call to FCM for single Data Message...')
            try:
                result = self.push_service.single_device_data_message(registration_id=reg_id_list[0],
                                                                  data_message=data_message)
            except Exception as e:
                self.logger.debug(e)
                return None
        else:
            self.logger.debug('Making call to FCM for multiple Data Messages...')
            try:
                result = self.push_service.multiple_devices_data_message(registration_ids=reg_id_list,
                                                                     data_message=data_message)
            except Exception as e:
                self.logger.debug(e)
                return None

        return result

    # Is there a better way to do this?
    def get_clean_data_array(self, shape):
        
#        ret = np.empty(shape, dtype=object)
        # This has problems : https://stackoverflow.com/questions/33983053/how-to-create-a-numpy-array-of-lists
#        ret.fill([])
        '''
        IMPORTANT! The first element (index 0) will be None. Use lists starting from 1
        '''
        
        linear_size = 1
        for s in shape:
            linear_size *= s
        ret = np.empty((linear_size,), dtype=object)    
        for i,v in enumerate(ret):
            ret[i] = list([])        
        # finally, reshape the matrix
        ret = ret.reshape(shape)
        return ret
    
    def read_user_id(self, u_id):
        if u_id is None or u_id == '':
            return ''
        
        algorithm = sha2()
        algorithm.update(u_id.encode())
        return algorithm.hexdigest().upper()
    
    def validate_intakes(self, med, dose, cur_session):
        # Oh boy...
        validation_date = parser.parse(med.validation_date)
        start_date = validation_date + timedelta(days=1)
        med.validation_date = (datetime.now() - timedelta(days=1)).isoformat()
        
        intakes = cur_session.query(Intake).filter(Intake.med_id == med.med_id).filter(Intake.planned_date > validation_date).all()
        ideal_intake_dates = self.get_ideal_intake_dates(dose, start_date)
        intake_dates_present = set([parser.parse(x.planned_date) for x in intakes])
        missed_intake_dates = [x for x in ideal_intake_dates if x not in intake_dates_present]
        
        missed_intakes = [Intake(med_id=med.med_id,
                                 planned_date=x.isoformat(),
                                 intake_status=3) for x in missed_intake_dates]
        
        cur_session.add_all(missed_intakes)
        cur_session.commit()
    
    def get_ideal_intake_dates(self, dose, start_date):
        ideal_intakes = []
        
        def get_prev_dosage_date(days, cur_date):
            cur_day_idx = cur_date.weekday()
            prev_day_idx = -1
            for i in range(len(days)-1, -1, -1):
                if days[i] < cur_day_idx:
                    prev_day_idx = i
                    break
            prev_day_delta = (cur_day_idx-days[prev_day_idx]+7)%7
            td = timedelta(days=prev_day_delta)
            return cur_date - td
        
        dosage_days = [self.all_days.index(x) for x in dose.get_days()]
        
        ideal_times = [get_prev_dosage_date(dosage_days, 
                                            parser.parse(tim)) for tim in dose.get_times()]
        ideal_times.reverse()
        while ideal_times[0].date() >= start_date.date():
            ideal_intakes.extend(ideal_times)
            ideal_times = [get_prev_dosage_date(dosage_days, 
                                                tim) for tim in ideal_times]
        
        return reversed(ideal_intakes)
        
        
        
