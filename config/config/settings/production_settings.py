import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['ticcapi.servatom.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'pgdb',
        'PORT': '5432',
    },

}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = '/home/vibha/ticc/static/'

# CSRF SETTINGS
CSRF_TRUSTED_ORIGINS = ['https://*ticcapi.servatom.com']



# CORS SETTINGS
CORS_ALLOWED_ORIGINS = [
    # Add the origins/URLs that need to access your API
    #'http://localhost:3000',  # Example: React development server URL
    'https://ticc.servatom.com',   # Example: Your production frontend URL
]


# add authorization header 
CORS_ALLOW_HEADERS = [
    'Authorization',
    'Content-Type',
]