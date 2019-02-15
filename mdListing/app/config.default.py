from pymongo import MongoClient

class Config(object):
    DB_CLIENT = MongoClient(
        'your_host',
        port=8080,
        username='your_username',
        password='your_password',
        authSource='your_authorization_db',
        authMechanism='SCRAM-SHA-256'
    )

    DB = DB_CLIENT['your_authorization_db']

    # Setting up the collections names to target
    BIBS = DB['your bibliographic collection']
    AUTHS = DB['your authority collection']
    
class ProductionConfig(Config):
    DEBUG = False
    
class DevelopmentConfig(Config):
    # Provide overrides for production settings here.
    DEBUG = True