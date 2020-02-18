import discord

from typing import Dict
from core.bot import Bot
from core.command_result import CommandResult
from core.modulebase import ModuleBase
from core.command import Command
from core.permissions import Permission
from .models import SPPermissions


class RestartCommand(Command):
    name = "restart"
    description = "Stops bot and allow bash script to restart it"
    sp_permissions = {Permission.OWNER}

    def __init__(self, bot: Bot):
        self.bot = bot

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        from core.module_manager import ModuleManager
        ModuleManager().force_unload()
        try:
            self.bot.loop.run_until_complete(self.bot.logout())
        except Exception:
            pass
        return CommandResult.success


class Module(ModuleBase):
    name = "BaseModule"
    description = "Basic module for minimal functionality"

    def on_load(self, bot: Bot):
        self.register(RestartCommand(bot))
