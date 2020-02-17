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


def start():
    start_time = time.time()
    bot = Bot()
    module_manager = ModuleManager()
    logger = Logger(app="Core", thread="Main")
    logger.log(2, "Starting %s bot with %s %s" % (colored("Fusion", "magenta"),
                                                  colored("Discord API", "blue"),
                                                  colored("v" + discord.__version__, "green")))
    logger.info("Loading modules from \"%s\" directory" % modules_dir)
    for file in os.listdir(modules_dir):
        if os.path.isdir(modules_dir + "/" + file) and os.path.exists(modules_dir + "/" + file + "/__init__.py"):
            module = __import__("%s.%s" % (modules_dir, file), globals(), locals(),
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
