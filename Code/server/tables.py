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
from sqlalchemy import Column, String, Integer
from dateutil import parser
Base = declarative_base()

class Install(Base):
    __tablename__ = 'installs'
    
    push_id = Column(String(200))
    install_id = Column(String(100), primary_key=True)
    user_id = Column(String(100), primary_key=True)
    
    def __repr__(self):
        return '<Install(user_id="%s", push_id="%s", install_id="%s")>' % (
                self.user_id, 
                self.push_id, 
                self.install_id)
    
class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String(100), primary_key=True)
    patient_id = Column(String(100))
    
    def __repr__(self):
        return '<User(user_id="%s", patient_id="%s")>' % (
                self.user_id,
                self.patient_id)
    

class Medication(Base):
    __tablename__ = 'medications'
    
    user_id = Column(String(100))
    med_id = Column(Integer, primary_key=True)
    med_name = Column(String(100))
    dosage_id = Column(Integer)
    validation_date = Column(String(40))
    
    def __repr__(self):
        return '<Medication(med_id="%s", med_name="%s", user_id="%s", dosage="%s")>' % (
                self.med_id,
                self.med_name,
                self.user_id,
                self.dosage_id
                )

class Dosage(Base):
    __tablename__ = 'dosage'
    
    dosage_id = Column(Integer, primary_key=True)
    days = Column(String(25*7))
    times = Column(String(10*7))
    
    def __repr__(self):
        return '<Dosage(dosage_id="%s", days="%s", times="%s")>' % (
                self.dosage_id,
                self.days,
                self.times)
        
    def get_days(self):
        return self.days.split(',')
    
    def get_times(self):
        return self.times.split(',')
    
class Intake(Base):
    __tablename__ = 'intakes'
    
    med_id = Column(Integer)
    intake_id = Column(Integer, primary_key=True)
    planned_date = Column(String(40))
    actual_date = Column(String(40))
    intake_status = Column(Integer)
    
    def __repr__(self):
        return '<Intake(intake_id="%s", med_id="%s", planned_date="%s", actual_date="%s", intake_status="%s")>' % (
                self.intake_id,
                self.med_id,
                self.planned_date, 
                self.actual_date,
                self.intake_status)
    
    #todo: Implement logic to get intake_status, dummy logic below 
    def get_status(self):
        a_d = parser.parse(self.actual_date)
        p_d = parser.parse(self.planned_date)
        
        if a_d > p_d:
            return 0
        return 1

class SensorReading(Base):
    __tablename__ = 'sensorreadings'
    
    reading_id = Column(Integer, primary_key=True)
    user_id = Column(String(100))
    med_id = Column(Integer)
    data = Column(String(100))
    
    
    def __repr__(self):
        return '<SensorReadings(user_id="%s", med_id="%s", data="%s")>' % (
                self.user_id,
                self.med_id,
                self.data)
    
