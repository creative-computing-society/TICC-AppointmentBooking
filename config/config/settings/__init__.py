import os
from dotenv import load_dotenv

load_dotenv()

# Get the 'STAGE' environment variable
stage = os.environ.get('STAGE')

# Choose the settings file based on the 'STAGE' value
if stage == 'DEVELOPMENT':
    from .development_settings import *
elif stage == 'PRODUCTION':
    from .production_settings import *
else:
    raise ValueError('Please set the STAGE environment variable')