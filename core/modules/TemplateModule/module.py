import discord
from core import ModuleBase, CommandResult, Command, Bot, DotDict, EventListener


class TemplateCommand(Command):
    name = "hello"
    description = "Template command"

    async def execute(self, message: discord.Message, args: list, keys: DotDict) -> CommandResult:
        await message.channel.send("Hello!")
        return CommandResult.success


class Module(ModuleBase):
    name = "TemplateModule"
    description = "Module TemplateModule"

    @EventListener
    def on_load(self, bot: Bot):
        self.register(TemplateCommand(bot))

    @EventListener
    async def run(self, bot: Bot):
        pass
