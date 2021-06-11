import os
from dotenv import dotenv_values
from .credentials_decrypt import decrypt_email_credential

ENV = os.getenv("ENV", default="local")

# pylint: disable=too-few-public-methods
class DefDictToObject():
    env = ENV

    def __init__(self, myDict):
        for key, value in myDict.items():
            print(f"{key} : {value}")
            if type(value) == dict:
                setattr(self, key, DefDictToObject(value))
            else:
                setattr(self, key, value)


config = DefDictToObject({
    **dotenv_values("config/app.default.env"),
    **dotenv_values(f"config/app.{ENV}.env"),
    **dotenv_values(f"config/app_email_listener.{ENV}.env"),
    # **os.environ,
})


config = decrypt_email_credential(config)
