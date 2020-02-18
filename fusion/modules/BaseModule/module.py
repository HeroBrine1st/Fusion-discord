import discord

from typing import Dict
from fusion.bot import Bot
from fusion.command import Command
from fusion.command_result import CommandResult
from fusion.modulebase import ModuleBase
from fusion.permissions import SPPermission  # , DiscordPermission


class RestartCommand(Command):
    name = "restart"
    description = "Stops bot and allow bash script to restart it"
    # permissions = {DiscordPermission.ADMINISTRATOR}
    sp_permissions = {SPPermission.OWNER}

    def __init__(self, bot: Bot):
        self.bot = bot

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        from fusion.module_manager import ModuleManager
        await ModuleManager().unload()
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
