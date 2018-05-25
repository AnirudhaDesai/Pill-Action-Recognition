# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 18:45:20 2018

@author: amitrc
"""
from collections import defaultdict
from predictor_factory import PredictorFactory

class PredictionService():
    m_twist, m_dispense, m_h2m, m_w2m = None, None, None, None
    db_session_factory = None
    helper = None
    model_type = None
    TIMEOUT_WINDOW = None # timeout for predict status in milliseconds
      
    user_predict_status = None
    features_to_use = []
    touch_threshold = None
    predictor = None
    
    def __init__(self):
        pass
    
    @staticmethod
    def start_service(sf, hlp):
        PredictionService.db_session_factory = sf
        PredictionService.helper = hlp
        PredictionService.TIMEOUT_WINDOW = hlp.get_config('model', 'timeout')
        PredictionService.predictor = PredictorFactory.create_predictor(hlp)
        
        PredictionService.user_predict_status = defaultdict(lambda : (hlp.STATUS_NO, -1))     # latest (status,time) of predicted "yes"
        
        
    @staticmethod
    def predict(medicine_id, user_id, data, touch_data, time):
        '''
        medicine_id : 
        user_id:
        data: nd array. data from accel,gyro.  
        touch_data = list of tuples [(state, timestamp)]
        time : start time of data window. To be stored in database if predicted
        '''        
        # check if prediction to be done based on status.
        helper = PredictionService.helper
        logger = helper.logger
        logger.debug('Prediction initiated for medicine : %s', medicine_id)
        if not PredictionService.is_predicted(medicine_id, time):
            prediction = PredictionService.predictor.predict((data, touch_data))
            
            if prediction == True:
                cur_session = PredictionService.db_session_factory()
                installs = helper.get_all_installs(cur_session, 
                                                    u_id=user_id)
                meds = helper.get_all_medications(cur_session, 
                                                  m_id=medicine_id)[0]
                
                push_ids = []
                for install in installs:
                    push_ids.append(install.push_id)
                
                print('True Intake Detected, Sending push notification to ', len(push_ids), ' Devices!!')
                helper.send_push_notification(push_ids, 
                                              {'message': 'Intake detected for - user: ' + user_id + ', medicine: ' + meds.med_name})
                # update medicine prediction status
                PredictionService.set_status(helper.STATUS_YES, medicine_id, time)
                logger.debug('Push Notification sent successfully!!')
                cur_session.close()
                    
    @staticmethod
    def is_predicted(med_id, time):
        #check if the prediction is already made for the user 
        # to be a 'Y' in the given window. If so, do not predict again.
        
        med_status = PredictionService.user_predict_status[med_id]
        
        if med_status[0] == PredictionService.helper.STATUS_NO:
            return False
        # latest prediction was true. check if within the window
        if time - med_status[1] > PredictionService.TIMEOUT_WINDOW:
            return False
        
        return True

    @staticmethod
    def set_status(status, med_id, time):
        # change status of the user. Can be called after prediction, after 
        # user replied to notification        
        PredictionService.user_predict_status[med_id] = (status, time)
    