from base import *
from base import INSTALLED_APPS as INSTALLED_APPS_BASE


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'meetupbasket',
        'USER': 'nzupec',
    }
}

# Application definition
INSTALLED_APPS = INSTALLED_APPS_BASE + (
    'debug_toolbar',
)

# Cache settings
# https://docs.djangoproject.com/en/1.7/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'cache_table',
    }
}

