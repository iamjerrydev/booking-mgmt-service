import boto3
import os
import logging
import jwt

from fastapi import HTTPException

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

client = boto3.client("cognito-idp")

def initiate_authentication(username, password):
    ret = client.initiate_auth(ClientId=os.environ["CLIENT_ID"], 
                        AuthFlow='USER_PASSWORD_AUTH', 
                        AuthParameters={'USERNAME': username, 
                                        'PASSWORD': password})
    return ret

def validate_user(token):
    try:
        if token:
            user = client.get_user(AccessToken=token)
            sub = ''
            for attr in user['UserAttributes']:
                if attr['Name'] == 'sub':
                    sub = attr['Value']
                    break
            return "shop_" + sub.replace("-", "")
        else:
            logging.info("Invalid Token")
            raise HTTPException(status_code=401, detail="Invalid Token")
    except Exception as error:
        logging.info("Authentication Error: {}.".format(error))
        raise HTTPException(status_code=401, 
                            detail="Authentication Error: {}".format(str(error)))



