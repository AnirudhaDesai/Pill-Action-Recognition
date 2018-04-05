# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 16:24:08 2018

@author: anirudha
"""
import requests

class Helpers:
    def __init__(self):
        pass
    
    def build_url(addr,*args):
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
    
        return url
    
    def get_request(url,params=None):
        '''
    
        :param url: url to send the get request
        :param params: params to append to the query
        :return: response from the server
        '''
        response = None
    
        try:
            response = requests.get(url, params=params)
    
        except Exception as e:
            print(e)
    
        return response
