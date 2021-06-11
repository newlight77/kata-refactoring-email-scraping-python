from shared.crypto_util.crypto_class import Crypto

def decrypt_email_credential(config):
    #email = crypto.encrypt_message(config.EMAIL).__str__()
    #password = crypto.encrypt_message(config.EMAIL_PASSWORD).__str__()
    #print(f"{email} : {password}")

    # encrypted username and password
    email = b'gAAAAABgwn-WrAORAMV-SwhfGrha3Ol2Yu7ACfynz4jcyCMvDaxs0cKupWDzpUxF4nBsfOOhnpVDb_F5yta5rV03PbDt-GcL2DRCTNxZ3Fji17fND3FrwU4='
    password = b'gAAAAABgwn-W-GRLshqDOpD-2b3aLTIYoFGtCLML8kUSU9UR3P0lxDRHn49XurTU_x_00dNyWBimwbOtuiyepNrkyzG5cGER3w=='

    crypto = Crypto(secretFile="config/crypto_secret.key");

    config.EMAIL = crypto.decrypt_message(email)
    config.EMAIL_PASSWORD = crypto.decrypt_message(password)
    
    return config
