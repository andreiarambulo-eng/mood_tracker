import os
from decouple import config

APP_NAME = config('APP_NAME', default='Mood Tracker API')
APP_HOST = config('APP_HOST', default='0.0.0.0')
APP_PORT = config('APP_PORT', default='8000')
APP_ENVIRONMENT = config('APP_ENVIRONMENT', default='production')

# SQLite database path — /tmp for serverless (Vercel), ./data for Docker/local
_default_db_dir = '/tmp' if os.environ.get('VERCEL') else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(_default_db_dir, exist_ok=True)
DATABASE_PATH = config('DATABASE_PATH', default=os.path.join(_default_db_dir, 'mood_tracker.db'))
