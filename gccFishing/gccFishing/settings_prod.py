from .settings import *

DEBUG = False
THUMBNAIL_DEBUG = False




DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'gccfishingdb',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'hammad',
        'PASSWORD': 'quakeroats9',
        'HOST': '127.0.0.1',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',
        'OPTIONS':{'autocommit':True,},                      # Set to empty string for default.
    }
}


