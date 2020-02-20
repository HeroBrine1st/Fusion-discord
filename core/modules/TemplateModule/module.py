import discord

from typing import Dict
from core import ModuleBase, CommandResult, Command, Bot


class TemplateCommand(Command):
    name = "hello"
    description = "Template command"

    async def execute(self, message: discord.Message, args: list, keys: Dict[str, bool]) -> CommandResult:
        await message.channel.send("Hello!")
        return CommandResult.success


class Module(ModuleBase):
    name = "TemplateModule"
    description = "Module TemplateModule"

    def on_load(self, bot: Bot):
        self.register(TemplateCommand(bot))

    async def run(self, bot: Bot):
        pass
