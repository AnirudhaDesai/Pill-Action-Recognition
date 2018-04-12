# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 16:24:08 2018

@author: anirudha
"""
import requests
import json

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
