# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 16:24:08 2018

@author: anirudha
"""
import requests

import json

from tables import Install
from pyfcm import FCMNotification


class Helpers:
    def __init__(self,flask_app):
        self.logger = flask_app.logger
        apikey = "AAAAgOfyS6s:APA91bH0GGnd4Xvw_pWMDpGmsQrR79CU8_bOmDj2QsHyrpua89dwV_UUAcJNRELByd_uikq4Hd5oI-ik6uWoW9i4w3qgtdqqg8TYKwwhAg-HllaBKoIdAy9yF1tvIGaAUvXGLtdIzTqF"                 # api key from FCM for the app
        self.push_service = FCMNotification(api_key = apikey)

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
        u_id = request.args.get('u_id', None)
        i_id = request.args.get('i_id', None)
        p_id = request.args.get('p_id', None)
        
        if i_id == None and p_id == None and u_id == None:
            return None
        
        if i_id != None:
            cur_installs = cur_session.query(Install).filter(Install.install_id == i_id).all()
        elif u_id != None:
            cur_installs = cur_session.query(Install).filter(Install.user_id == u_id).all()
        else:
            cur_installs = cur_session.query(Install).filter(Install.push_id == p_id).all()
        
        if len(cur_installs) == 0:
            return None
        return cur_installs

    def send_push_notification(reg_id_list, data_message=None):
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
