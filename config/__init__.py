import os
from dotenv import dotenv_values
from .credentials_decrypt import decrypt_email_credential
from shared.collections_util.dict_util import DefDictToObject

ENV = os.getenv("ENV", default="local")

config = DefDictToObject({
    'env': ENV,
    **dotenv_values("config/app.default.env"),
    **dotenv_values(f"config/app.{ENV}.env"),
    **dotenv_values(f"config/app_email_listener.{ENV}.env"),
    # **os.environ,
})


config = decrypt_email_credential(config)
