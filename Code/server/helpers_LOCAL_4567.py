# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 16:24:08 2018

@author: anirudha
"""
import requests
import json
from tables import Install

class Helpers:
    def __init__(self,flask_app):
        self.logger = flask_app.logger
    
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
