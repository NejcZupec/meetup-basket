from base import *


DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'meetupbasket',
        'USER': 'meetupbasket',
        'PASSWORD': get_env_variable('DB_PASSWORD'),
        'HOST': 'localhost',
        'DB': 'meetupbasket',
    }
}

# Local static files
STATIC_ROOT = os.path.join(PROJECT_DIR, 'staticfiles')
