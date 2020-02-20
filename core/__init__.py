# For one "import core" and nothing else.
from core.command import Command
from core.command_result import CommandResult
from core.exceptions import *
from core.module_manager import ModuleManager
from core.modulebase import ModuleBase
from core.permissions import DiscordPermission, FuturePermission
from core.protocol import Client

import core.protocol
import math
import time
import traceback
import django
import discord

from django.core.management import call_command
from termcolor import colored
from bot.settings import *
from core.bot import Bot
from core.command_result import CommandResult
from core.exceptions import *
from core.module_manager import ModuleManager
from core.logger import Logger

logger = Logger(app="Core", thread="Main")


def load_apps_from_dir(mod_dir, ignore=None):
    from bot.settings import INSTALLED_APPS
    if ignore is None:
        ignore = {}
    for file in os.listdir(mod_dir):
        if file in ignore:
            continue
        path = mod_dir + "/" + file
        if os.path.isdir(path) and os.path.exists(path + "/module.py"):
            INSTALLED_APPS.append(path.replace("/", "."))


def load_modules_from_dir(mod_dir, ignore=None):
    if ignore is None:
        ignore = {}
    for file in os.listdir(mod_dir):
        if file in ignore:
            continue
        path = mod_dir + "/" + file
        if os.path.isdir(path) and os.path.exists(path + "/module.py"):
            module = __import__(path.replace("/", ".") + ".module", globals(), locals(),
                                fromlist=["Module", "load_module"])
            do_load = True
            if hasattr(module, "load_module"):
                do_load = module.load_module
            if do_load and hasattr(module, "Module"):
                instance = module.Module()
                ModuleManager().add_module(instance)
                logger.log(2, "Loaded module \"%s\"" % instance.name)


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def parse(raw):
    _args_0 = []
    _keys_0 = DotDict({})
    for elem in raw:
        if elem.startswith("--"):
            elem = elem[1:]
            _key_0, _value_0 = elem, True
            if ~elem.find("="):
                res = args_regex.search(elem)
                _key_0 = res.group(1)
                _value_0 = res.group(2)
            _keys_0[_key_0] = _value_0
        elif elem.startswith("-"):
            for char in elem[1:]:
                _keys_0[char] = True
        else:
            _args_0.append(elem)
    return _args_0, _keys_0


def start():
    start_time = time.time()
    bot = Bot()
    module_manager = ModuleManager()
    logger.log(2, "Starting %s bot with %s %s" % (colored("Fusion", "magenta"),
                                                  colored("Discord API", "blue"),
                                                  colored("v" + discord.__version__, "green")))
    logger.info("Setting up django")
    django.setup()
    logger.info("Loading modules from \"%s\" and \"core/modules\" directories" % modules_dir)
    load_modules_from_dir("core/modules", ignore={"TemplateModule"})
    load_modules_from_dir(modules_dir)

    module_manager.initialize(bot)
    logger.info("Setting up django models")
    for app in INSTALLED_APPS:
        call_command("makemigrations", app.split(".")[-1:][0])
    call_command("migrate")
    logger.info("Connecting to discord")

    @bot.event
    async def on_ready():
        logger.info("Logged into Discord as \"%s\"." % bot.user.name)
        logger.info("Running modules..")
        await module_manager.run_modules(bot)
        logger.info("Deploying threads and starting protocol processing")
        core.protocol.deploy()

        print("")
        logger.log(2, "INIT FINISHED! (took %ss)" % math.floor(time.time() - start_time))
        logger.log(2, "Loaded Modules: %s" % module_manager.modules_count)
        logger.log(2, "Loaded Commands: %s" % module_manager.commands_count)
        logger.log(2, "Listening %s:%s" % (listen_ip if listen_ip != "" else "0.0.0.0", listen_port))
        print("")

    @bot.event
    async def on_message(message: discord.Message):
        for _, mod in list(module_manager.modules.items()):
            await mod.on_message(message, bot)
        if not message.content.startswith(cmd_prefix):
            return

        args = message.content.split()
        cmd = args.pop(0)[len(cmd_prefix):].lower()

        if cmd not in module_manager.commands:
            await bot.send_error_embed(message.channel, "Команда \"%s\" не найдена." % cmd,
                                       "Команда не найдена")
            return

        command = module_manager.commands[cmd]
        if command.guild_lock and message.guild.id not in command.guild_lock:
            await bot.send_error_embed(message.channel, "Команда \"%s\" недоступна на данном сервере." % cmd,
                                       "Команда не найдена")
            return
        logger.info(
            "Выполнение команды %s от %s (%s)." % (repr(message.content), str(message.author), message.author.id))
        args_1, keys = parse(args[1:])
        try:
            if not module_manager.check_permissions(message.author.guild_permissions, command.permissions) \
                    or not module_manager.check_sp_permissions(message.author.id, command.future_permissions):
                embed: discord.Embed = bot.get_error_embed("У вас недостаточно прав для выполнения данной команды",
                                                           "Нет прав!")
                required_perms = "\n".join(perm.special_name for perm in
                                           sorted(command.permissions, key=lambda x: x.value) +
                                           sorted(command.future_permissions, key=lambda x: x.value))
                embed.add_field(name="Необходимые права:",
                                value=required_perms)
                await message.channel.send(embed=embed)
                await message.add_reaction(emoji_warn)
                return
            result = await command.execute(message, args_1, keys)
        except discord.Forbidden:
            await message.add_reaction(emoji_error)
            await bot.send_error_embed(message.channel, "У бота нет прав!")
        except AccessDeniedException:
            await message.add_reaction(emoji_warn)
            await bot.send_error_embed(message.channel, "У вас недостаточно прав для выполнения данной команды",
                                       "Нет прав!")
        except CommandException as e:
            await message.add_reaction(emoji_warn)
            await bot.send_error_embed(message.channel, str(e), e.title)
        except Exception:
            await bot.send_error_embed(message.channel, "```\n%s\n```" % traceback.format_exc(),
                                       "⚠ Криворукий уебан, у тебя ошибка! ⚠")
            await message.add_reaction(emoji_error)
        else:
            if result == CommandResult.success:
                await message.add_reaction(emoji_ok)
            elif result == CommandResult.arguments_insufficient:
                embed: discord.Embed = bot.get_error_embed(title="Недостаточно аргументов!")
                embed.add_field(name="%s%s %s" % (cmd_prefix, command.name, command.arguments),
                                value=command.description)
                await message.channel.send(embed=embed)
                await message.add_reaction(emoji_warn)

    @bot.event
    async def on_message_delete(message: discord.Message):
        for _, mod in list(module_manager.modules.items()):
            await mod.on_message_delete(message, bot)

    @bot.event
    async def on_message_edit(before: discord.Message, after: discord.Message):
        for _, mod in list(module_manager.modules.items()):
            await mod.on_message_edit(before, after, bot)

    @bot.event
    async def on_member_remove(member: discord.Member):
        for _, mod in list(module_manager.modules.items()):
            await mod.on_member_remove(member, bot)

    @bot.event
    async def on_member_join(member: discord.Member):
        for _, mod in list(module_manager.modules.items()):
            await mod.on_member_join(member, bot)

    bot.run(discord_token)
