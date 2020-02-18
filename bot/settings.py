import os
import re

cmd_prefix = "/"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
listen_port = 51413
modules_dir = "modules"
INSTALLED_APPS = []
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

args_regex = re.compile(r"(.*?)=(.+)")
emoji_ok = "☑"
emoji_error = "🛑"
emoji_warn = "⚠"