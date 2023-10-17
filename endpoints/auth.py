import logging
from fastapi import HTTPException
from utils import *

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def method_verify_user(username, password):
    try:
        ret = initiate_authentication(username, password)
        logging.info("Login Successful for {}.".format(username))
        response = {
            'token': ret['AuthenticationResult']['AccessToken']
        }
        return response
    except Exception as error:
        logging.info("Login Error: {}.".format(error))
        raise HTTPException(status_code=400, 
                            detail="Login Error: {}".format(str(error)))
    