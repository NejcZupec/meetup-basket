from base import *

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'meetupbasket',
        'USER': 'nzupec',
    }
}

# Cache settings
# https://docs.djangoproject.com/en/1.7/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'cache_table',
    }
}

# Static files settings
STATICFILES_DIRS = (
    'djangobower.finders.BowerFinder',
)