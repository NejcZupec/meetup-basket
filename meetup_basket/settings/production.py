from base import *

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'meetupbasket',
        'USER': 'meetupbasket',
        'PASSWORD': get_env_variable('DB_PASSWORD'),
        'HOST': '',
        'DB': 'meetupbasket',
    }
}
