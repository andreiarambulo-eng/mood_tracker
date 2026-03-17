from decouple import config

APP_NAME = config('APP_NAME', default='Mood Tracker API')
APP_HOST = config('APP_HOST', default='0.0.0.0')
APP_PORT = config('APP_PORT', default='8000')
APP_ENVIRONMENT = config('APP_ENVIRONMENT', default='production')
CONNECTION_STRING = config('CONNECTION_STRING')
DATABASE_NAME = config('DATABASE_NAME', default='mood_tracker')
