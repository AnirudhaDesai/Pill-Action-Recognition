try:
    from google.oauth2 import id_token
    from google.auth.transport import requests
except Exception as e:
    print (e)


def verify_sign_in(token, hp):
#    responses = verify_sign_in_easy(token,client_id,hp)
    userid = None
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        hp.logger.debug(hp.client_id)
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), hp.client_id)
    
        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')
    
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
    
        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')
    
        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        
    except ValueError as e:
    # Invalid token
        hp.logger.error('Sign in failed with error : %s',str(e))
        
    hp.logger.debug('Response from google token info : %s', str(userid))
    return userid
    

def verify_sign_in_easy(token, client_id,hp):
    hp.logger.info('Sending request to Google..')
    
    url = "https://www.googleapis.com/oauth2/v3/tokeninfo"
    data = {'id_token':str(token)}
#    while True:
#        a = 1
    response = hp.get_request(url,data)
    
    hp.logger.error('Response from google : %s ', str(response))
    
    return response
    
