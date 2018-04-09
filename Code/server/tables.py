# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 20:40:36 2018

@author: amitrc
"""

'''
Add all tables to be used to this file as classes.
Make sure each class inherits from Base.
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
Base = declarative_base()

class Install(Base):
    __tablename__ = 'user'
    
    user_id = Column(String)
    push_id = Column(String)
    install_id = Column(String, primary_key=True)
    
    def __repr__(self):
        return '<User(user_id="%s", push_id="%s", install_id="%s">' % (self.user_id, 
                                                                       self.push_id, 
                                                                       self.install_id)
    
