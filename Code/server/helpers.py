# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 16:24:08 2018

@author: anirudha
"""
import requests

import json
import numpy as np
import os
from tables import Install, Medication
from pyfcm import FCMNotification
import configparser
from hashlib import sha256 as sha2
import copy

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
        self.load_config()        
    
    def load_config(self):
        config = configparser.ConfigParser()
        cp = os.path.join(os.path.dirname(__file__),"./")
        configPath = cp + 'server_config.ini'
        config.read(configPath)
        self.client_id = config['Basic']['client_id']

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
            result = self.push_service.single_device_data_message(registration_id=reg_id_list[0],
                                                                  data_message=data_message)
        else:
            result = self.push_service.multiple_devices_data_message(registration_ids=reg_id_list,
                                                                     data_message=data_message)

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
        return algorithm.hexdigest()
        
