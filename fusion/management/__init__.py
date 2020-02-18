import os
import sys
from django.core.management import execute_from_command_line as efcl, call_command as call
from bot import settings
from fusion import start, load_apps_from_dir


def call_command(command, *args):
    if command == "runbot" or command == "runserver":
        start()
    elif command == "startapp":
        name = args[0]
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
        with open("fusion/modules/TemplateModule/module.py", "r") as f:
            with open(folder + "module.py", "w") as f2:
                f2.write(f.read().replace("TemplateModule", name))
        with open("fusion/modules/TemplateModule/models.py", "r") as f:
            with open(folder + "models.py", "w") as f2:
                f2.write(f.read())
    elif command == "custom_makemigrations":
        for app in settings.INSTALLED_APPS:
            call("makemigrations", app.split(".")[-1:][0])
    else:
        efcl(sys.argv)


def execute_from_command_line(argv):
    load_apps_from_dir("fusion/modules", ignore={"TemplateModule"})
    load_apps_from_dir(settings.modules_dir)
    command = argv[1]
    args = argv[2:]
    if command == "startproject":
        name = args[0] if len(args) > 0 else "fusion"
        from pkg_resources import resource_string
        resource_string("fusion.management", "manage.py")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("FUSION_SETTINGS_MODULE"))
        call_command(command, args)
