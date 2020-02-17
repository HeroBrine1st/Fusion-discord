import os

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
listen_port = 51413
modules_dir = "modules"
INSTALLED_APPS = [
    "core.modules.base",
]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
