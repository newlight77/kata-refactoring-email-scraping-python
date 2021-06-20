from shared.crypto_util.crypto_class import Crypto

def decrypt_email_credential(config):
    crypto = Crypto(secretFile="config/crypto_secret.key")

    # encrypted gmail
    email = b'gAAAAABgz6ixReJs7wOJV5ng-Pl2-bq09KpxnjexKCgQPJ4TMimP_6BldOA-20o-zzRIniJ2MzJhUGit-kHl0KQxnJih81CfEBPbVsP0zaQZs0dozNh1-XU='
    password = b'gAAAAABgz6ixAwPaJ1gmCMvCbBzKcWRM3Nx32A7QbwHtGkuokhYfHxPG1CsCqoQbYEXRlxgq5jzuco5af_W29jOhdyIvnRHDyV3D_Ocpq1NzeFyu2lLGT_c='

    # encrypted
    #email = b'gAAAAABgwn-WrAORAMV-SwhfGrha3Ol2Yu7ACfynz4jcyCMvDaxs0cKupWDzpUxF4nBsfOOhnpVDb_F5yta5rV03PbDt-GcL2DRCTNxZ3Fji17fND3FrwU4='
    #password = b'gAAAAABgwn-W-GRLshqDOpD-2b3aLTIYoFGtCLML8kUSU9UR3P0lxDRHn49XurTU_x_00dNyWBimwbOtuiyepNrkyzG5cGER3w=='

    #email = crypto.encrypt_message(config.EMAIL).__str__()
    #password = crypto.encrypt_message(config.EMAIL_PASSWORD).__str__()
    #print(f"{email} : {password}")

    print(f"{config.EMAIL} : {config.EMAIL_PASSWORD}")

    config.EMAIL = crypto.decrypt_message(email)
    config.EMAIL_PASSWORD = crypto.decrypt_message(password)

    return config
