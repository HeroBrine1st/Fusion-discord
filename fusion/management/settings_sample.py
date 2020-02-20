import os
import re

SECRET_KEY = "SECRET_KEY_HERE"
INSTALLED_APPS = []
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

discord_token = "PLACE_YOUR_TOKEN_HERE"
listen_port = 51413
owner_id = 0
listen_ip = ""
cmd_prefix = "/"
args_regex = re.compile(r"(.*?)=(.+)")
emoji_ok = '✅'
emoji_error = '🛑'
emoji_warn = '⚠'
