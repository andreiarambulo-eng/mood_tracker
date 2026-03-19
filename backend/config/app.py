import os
from decouple import config

APP_NAME = config('APP_NAME', default='Mood Tracker API')
APP_HOST = config('APP_HOST', default='0.0.0.0')
APP_PORT = config('APP_PORT', default='8000')
APP_ENVIRONMENT = config('APP_ENVIRONMENT', default='production')

# MongoDB connection
CONNECTION_STRING = config('CONNECTION_STRING', default='mongodb://localhost:27017/')
DATABASE_NAME = config('DATABASE_NAME', default='mood_tracker')
