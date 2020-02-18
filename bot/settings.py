import os
import re

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
INSTALLED_APPS = []
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

discord_token = os.environ.get("fusion_discord_token")
listen_port = 51413
modules_dir = "modules"
cmd_prefix = "/"
args_regex = re.compile(r"(.*?)=(.+)")
emoji_ok = '✅'
emoji_error = '🛑'
emoji_warn = '⚠'
