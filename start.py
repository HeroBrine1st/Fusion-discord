import discord
import django

from core.bot import Bot
from termcolor import colored
from core.module_manager import ModuleManager
from core.modules.base import Module as BaseModule
from libraries.logger import Logger
from params import *
from django.core.management import call_command

bot = Bot()
module_manager = ModuleManager()
logger = Logger(app="Core", thread="Main")
logger.log(2, "Starting %s bot with %s %s" % (colored("Fusion", "magenta"),
                                              colored("Discord API", "blue"),
                                              colored("v" + discord.__version__, "green")))
logger.info("Loading modules from \"%s\" directory" % modules_dir)
for file in os.listdir(modules_dir):
    if os.path.isdir(modules_dir + "/" + file) and os.path.exists(modules_dir + "/" + file + "/__init__.py"):
        module = __import__("%s.%s" % (modules_dir, file[:-3]), globals(), locals(),
                            fromlist=["Module", "load_module"])
        do_load = True
        if hasattr(module, "load_module"):
            do_load = module.load_module
        if do_load and hasattr(module, "Module"):
            instance = module.Module()
            module_manager.add_module(instance)
            logger.log(2, "Loaded module \"%s\"" % instance.name)
        module_manager.add_module(BaseModule())
        logger.log(2, "Loaded module \"BaseModule\"")
module_manager.initialize(bot)
logger.info("Note that modules have to add self path to params.INSTALLED_APPS when loaded.")
logger.info("Setting up database connection")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "params")
django.setup()
for app in INSTALLED_APPS:
    call_command("makemigrations", app.split(".")[-1:][0])
call_command("migrate")
