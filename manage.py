import os
import sys
from django.core.management import execute_from_command_line
from bot import settings
from core import start, load_apps_from_dir

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bot.settings")
load_apps_from_dir("core/modules", ignore={"TemplateModule"})
load_apps_from_dir(settings.modules_dir)
command = sys.argv[1]
if command == "runbot" or command == "runserver":
    start()
elif command == "startapp":
    name = sys.argv[2]
    if name.lower().endswith("module"):
        name = name.lower()
        mod_pos = name.find("module")
        name = name[0].upper() + name[1:mod_pos] + name[mod_pos].upper() + name[mod_pos + 1:]
    else:
        name = name[0].upper() + name[1:].lower() + "Module"
    folder = "modules/" + name + "/"
    if os.path.isdir(folder):
        print("Module \"%s\" already exists and installed." % name)
        exit(0)
    os.mkdir(folder)
    with open("core/modules/TemplateModule/module.py", "r") as f:
        with open(folder + "module.py", "w") as f2:
            f2.write(f.read().replace("TemplateModule", name))
    with open("core/modules/TemplateModule/models.py", "r") as f:
        with open(folder + "models.py", "w") as f2:
            f2.write(f.read())
else:
    execute_from_command_line(sys.argv)
