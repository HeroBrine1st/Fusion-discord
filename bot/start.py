import math
import time

import discord
import django

from core.bot import Bot
from termcolor import colored
from core.module_manager import ModuleManager
from core.modules.BaseModule import Module as BaseModule
from libraries.logger import Logger
from bot.settings import *
from django.core.management import call_command

logger = Logger(app="Core", thread="Main")


def load_modules_from_dir(mod_dir, ignore=None):
    if ignore is None:
        ignore = {}
    for file in os.listdir(mod_dir):
        if file in ignore:
            continue
        path = mod_dir + "/" + file
        if os.path.isdir(path) and os.path.exists(path + "/__init__.py"):
            module = __import__(path.replace("/", "."), globals(), locals(),
                                fromlist=["Module", "load_module"])
            do_load = True
            if hasattr(module, "load_module"):
                do_load = module.load_module
            if do_load and hasattr(module, "Module"):
                instance = module.Module()
                ModuleManager().add_module(instance)
                logger.log(2, "Loaded module \"%s\"" % instance.name)


def start():
    start_time = time.time()
    bot = Bot()
    module_manager = ModuleManager()
    logger.log(2, "Starting %s bot with %s %s" % (colored("Fusion", "magenta"),
                                                  colored("Discord API", "blue"),
                                                  colored("v" + discord.__version__, "green")))
    logger.info("Loading modules from \"%s\" and \"core/modules\" directory" % modules_dir)
    load_modules_from_dir("core/modules", ignore={"TemplateModule"})
    load_modules_from_dir(modules_dir)

    module_manager.initialize(bot)
    logger.info("Note that modules have to add self path to params.INSTALLED_APPS when loaded.")
    logger.info("Setting up database connection")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bot.settings")
    django.setup()
    for app in INSTALLED_APPS:
        call_command("makemigrations", app.split(".")[-1:][0])
    call_command("migrate")
    logger.info("Connecting to discord")

    @bot.event
    async def on_ready():
        logger.info("Logged into Discord as \"%s\"." % bot.user.name)
        logger.info("Running modules..")
        await module_manager.run_modules(bot)
        print("")
        logger.log(2, "INIT FINISHED! (took %ss)" % math.floor(time.time() - start_time))
        logger.log(2, "Loaded Modules: %s" % module_manager.modules_count)
        logger.log(2, "Loaded Commands: %s" % module_manager.commands_count)
        print("")

    bot.run(os.environ.get("fusion_discord_token"))
