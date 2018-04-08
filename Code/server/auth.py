

def verify_sign_in(id_token, hp):
    verify_sign_in_easy(id_token)

def verify_sign_in_easy(id_token,hp):
    print('Sending request ..')
    
    url = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
    responses = hp.get_request(url,params=id_token)
    return responses
    
