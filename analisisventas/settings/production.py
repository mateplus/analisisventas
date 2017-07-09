from .base import *
import mongoengine
from django.contrib.humanize.templatetags.humanize import intcomma
from mongoengine import *
#from mongoengine import connect


#AUTHENTICATION_BACKENDS = (
#    'mongoengine.django.auth.MongoEngineBackend',
#)
 
#SESSION_ENGINE = 'mongoengine.django.sessions'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']



DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
    }
}


#_MONGODB_USER='usr1'
#_MONGODB_PASSWD='12345'
#_MONGODB_HOST='localhost:27017'
#_MONGODB_NAME='admin'

_MONGODB_USER = 'usr'
_MONGODB_PASSWD = '12345'
_MONGODB_HOST = 'localhost:27017'
_MONGODB_NAME = 'ventasDB'

_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_NAME)

mongoengine.connect(_MONGODB_NAME, host=_MONGODB_DATABASE_HOST)

#connect('employeedb', username='my_username', password='secret_password')

	
# Application definition


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/'
SHORT_DATETIME_FORMAT='d/m/Y'

def currency(dollars):
    dollars = round(float(dollars), 2)
    return "$%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
