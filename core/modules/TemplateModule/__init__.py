import discord
import bot.settings as settings

from typing import Dict
from core.bot import Bot
from core.command_result import CommandResult
from core.modulebase import ModuleBase
from core.command import Command


class TemplateCommand(Command):
    name = "hello"
    description = "Template command"

    def __init__(self, bot: Bot):
        self.bot = bot

    async def execute(self, message: discord.Message, args: str, keys: Dict[str, bool]) -> CommandResult:
        await message.channel.send("Hello!")
        return CommandResult.success


class Module(ModuleBase):
    name = "TemplateModule"
    description = "Module TemplateModule"

    def on_load(self, bot: Bot):
        self.register(TemplateCommand(bot))
        settings.INSTALLED_APPS.append("modules.TemplateModule")

    def run(self, bot: Bot):
        pass
