import os
import re
import bot.secure

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
INSTALLED_APPS = []
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

protocol_encoding = "UTF-8"
discord_token = os.environ.get("fusion_discord_token")
listen_port = 51413
owner_id = 308653925379211264
listen_ip = ""
modules_dir = "modules"
cmd_prefix = "/"
args_regex = re.compile(r"(.*?)=(.+)")
emoji_ok = '✅'
emoji_error = '🛑'
emoji_warn = '⚠'

protocol_clients = {
    "default": {
        "AUTH_TOKEN": bot.secure.default_client_token,
        "GUILD_ID": 547876610032926757,
        "CHANNEL_ID": 668454176631554049,

    }
}
