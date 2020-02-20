import discord

from typing import Dict
from core.bot import Bot
from core.command import Command
from core.command_result import CommandResult
from core.modulebase import ModuleBase
from core.permissions import SPPermission  # , DiscordPermission
from core.module_manager import ModuleManager


class RestartCommand(Command):
    name = "restart"
    description = "Stops bot and allow bash script to restart it"
    # permissions = {DiscordPermission.ADMINISTRATOR}
    sp_permissions = {SPPermission.OWNER}

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        await ModuleManager().unload()
        try:
            self.bot.loop.run_until_complete(self.bot.logout())
        except Exception:
            pass
        return CommandResult.success


class HelpCommand(Command):
    name = "help"
    description = "Command list"

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        for command in ModuleManager().commands:
            pass
        return CommandResult.success


class Module(ModuleBase):
    name = "BaseModule"
    description = "Basic module for minimal functionality"

    def on_load(self, bot: Bot):
        self.register(RestartCommand(bot))
