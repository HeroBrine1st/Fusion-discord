import discord

from typing import Dict
from core.bot import Bot
from core.command import Command
from core.command_result import CommandResult
from core.modulebase import ModuleBase


class TemplateCommand(Command):
    name = "hello"
    description = "Template command"

    def __init__(self, bot: Bot):
        self.bot = bot

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        await message.channel.send("Hello!")
        return CommandResult.success


class Module(ModuleBase):
    name = "TemplateModule"
    description = "Module TemplateModule"

    def on_load(self, bot: Bot):
        self.register(TemplateCommand(bot))

    def run(self, bot: Bot):
        pass
