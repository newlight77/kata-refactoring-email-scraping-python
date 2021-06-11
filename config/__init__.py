import os
from dotenv import dotenv_values
from .credentials_decrypt import decrypt_email_credential
class defDictToObject(object):
    
    def __init__(self, myDict):
        for key, value in myDict.items():
            print(f"{key} : {value}")
            if type(value) == dict:
                setattr(self, key, defDictToObject(value))
            else:
                setattr(self, key, value)   


ENV = os.getenv("ENV", default="local")

config = defDictToObject({
    **dotenv_values("config/app.default.env"),  # load shared development variables
    **dotenv_values(f"config/app.{ENV}.env"),  # load specific variables
    **dotenv_values(f"config/app_email_listener.{ENV}.env"),  # load specific variables
    #**os.environ,  # override loaded values with environment variables
})

config.ENV = ENV

config = decrypt_email_credential(config)
