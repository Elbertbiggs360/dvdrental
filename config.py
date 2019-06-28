import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Config(object):
    DEBUG = False
    BASE_DIR = os.path.dirname(__file__)
    DB_NAME = os.environ.get('DB_NAME') or 'dvdrental'
    DB_USER = os.environ.get('DB_USER') or 'postgres'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_URI = os.environ.get('DB_URI') or 'postgresql://localhost/{}'.format(DB_NAME)

class Development(Config):
    DEBUG = True
    DEVELOPMENT = True

class Testing(Config):
    TESTING = True
    DB_URI = os.environ.get('TEST_DB') or 'postgresql://localhost/dvdtest'

class Production(Config):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False

app_config = {
    'development': Development,
    'testing': Testing,
    'production': Production
}
