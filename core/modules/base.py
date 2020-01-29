import discord

from typing import Dict
from core.bot import Bot
from core.command_result import CommandResult
from core.modulebase import ModuleBase
from core.command import Command
from core.permissions import Permission

class RestartCommand(Command):
    name = "restart"
    description = "Stops bot and allow bash script to restart it"
    sp_permissions = {Permission.OWNER}

    def __init(self, bot: Bot):
        self.bot = bot

    async def execute(self, message: discord.Message, args: str, keys: Dict[str, bool]) -> CommandResult:
        await self.bot.logout()
        return CommandResult.success

class Module(ModuleBase):
    name = "BaseModule"
    description = "Basic module for minimal functionality"

    def on_load(self, bot: Bot):

